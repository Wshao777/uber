#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <random>
#include <ctime>
#include <iomanip>
#include <map>
#include "nlohmann/json.hpp" // Assuming nlohmann/json.hpp is in the include path

using json = nlohmann::json;
using namespace std;

// Configuration structure
struct Config {
    struct Pricing {
        double km;
        double base_price;
        double achieved_price;
        double orders_per_hour;
    };
    map<string, Pricing> base_pricing = {
        {"near", {1.565, 68.0, 171.36, 10.0}},
        {"mid", {3.385, 73.0, 178.56, 5.5}},
        {"far", {8.25, 78.0, 186.24, 4.0}}
    };
    map<string, double> time_factor = {{"peak", 1.2}, {"off_peak", 0.8}};
    double achieved_threshold = 1.25;
    double abandon_rate = 0.15;
    double cost_percent = 0.3;
    double target_hourly_wage = 714.0;
    double target_hourly_wage_4day = 536.0;
    double k_factor = 9.412;
    double target_trips = 150.0;
    double target_trips_4day = 128.0;
    double bonus = 900.0;
    double tax_rate = 0.1;
    string bank_swift = "CHPYTWTP";
    string bank_account = "00210091602429";
};

class DynamicPricingSimulator {
private:
    Config config;
    mt19937 rng;
    uniform_real_distribution<double> dist;

public:
    DynamicPricingSimulator() : rng(static_cast<unsigned>(time(0))), dist(0.0, 1.0) {}

    bool is_peak_hour() {
        time_t now = time(nullptr);
        tm* ltm = localtime(&now);
        int hour = ltm->tm_hour;
        return (hour >= 7 && hour <= 10) || (hour >= 17 && hour <= 20);
    }

    json calculate_price(const string& distance_type, double achieved_ratio, double target_wage, const string& platform = "uber") {
        auto& base = config.base_pricing[distance_type];
        double time_factor = is_peak_hour() ? config.time_factor["peak"] : config.time_factor["off_peak"];
        double platform_weight = platform == "uber" ? 1.2 : 1.0;
        double abandon_rate = config.abandon_rate;

        double price = (achieved_ratio >= config.achieved_threshold)
            ? base.achieved_price * time_factor * platform_weight * (1 - abandon_rate * 0.2)
            : base.base_price * time_factor * platform_weight * (1 - abandon_rate * 0.2);

        double hourly_wage = price * base.orders_per_hour;
        double real_wage = hourly_wage * (1 - config.cost_percent);
        double supplement_km = (target_wage / base.orders_per_hour) / config.k_factor - base.km;
        double hours_to_target = (target_wage == config.target_hourly_wage ? config.target_trips : config.target_trips_4day) / base.orders_per_hour;
        double total_wage = hours_to_target * hourly_wage + config.bonus;

        json result = {
            {"distance_type", distance_type},
            {"price", round(price * 100) / 100},
            {"hourly_wage", round(hourly_wage * 100) / 100},
            {"real_wage", round(real_wage * 100) / 100},
            {"supplement_km", round(supplement_km * 1000) / 1000},
            {"hours_to_target", round(hours_to_target * 100) / 100},
            {"total_wage", round(total_wage * 100) / 100},
            {"platform", platform},
            {"tax", round(real_wage * config.tax_rate * 100) / 100},
            {"timestamp", to_string(time(nullptr))},
            {"bank_swift", config.bank_swift},
            {"bank_account", config.bank_account}
        };
        return result;
    }

    json simulate_orders(int hours, int target_trips, double target_wage) {
        vector<string> distance_types = {"near", "mid", "far"};
        vector<double> weights = {0.5, 0.3, 0.2};
        discrete_distribution<int> dist_type(weights.begin(), weights.end());

        json log = json::array();
        double total_wage = 0.0, total_real_wage = 0.0;
        int trips = 0;

        for (int h = 0; h < hours && trips < target_trips; ++h) {
            string platform = dist(rng) < 0.6 ? "uber" : "foodpanda";
            string distance_type = distance_types[dist_type(rng)];
            double achieved_ratio = (trips >= target_trips * 0.8) ? 1.25 : 1.0;
            bool is_fat_order = dist(rng) < 0.1;
            bool cross_bonus = (distance_type == "far" && dist(rng) < 0.2);

            json result = calculate_price(distance_type, achieved_ratio, target_wage, platform);
            if (is_fat_order) {
                result["price"] = result["price"].get<double>() + 200.0;
                result["supplement_km"] = result["supplement_km"].get<double>() + 8.0;
            }
            if (cross_bonus) {
                result["price"] = result["price"].get<double>() + 50.0;
                result["cross_bonus"] = 50.0;
            }
            result["hourly_wage"] = result["price"].get<double>() * config.base_pricing[distance_type].orders_per_hour;
            result["real_wage"] = result["hourly_wage"].get<double>() * (1 - config.cost_percent);
            result["tax"] = result["real_wage"].get<double>() * config.tax_rate;

            total_wage += result["hourly_wage"].get<double>();
            total_real_wage += result["real_wage"].get<double>();
            trips += static_cast<int>(config.base_pricing[distance_type].orders_per_hour);
            log.push_back(result);
        }

        json summary = {
            {"total_hours", hours},
            {"total_trips", trips},
            {"total_wage", round(total_wage * 100) / 100},
            {"total_real_wage", round(total_real_wage * 100) / 100},
            {"weekly_target_achieved", total_real_wage >= 20000.0},
            {"four_day_target_achieved", total_real_wage >= 12000.0 && hours <= 32}
        };
        log.push_back(summary);
        return log;
    }

    void save_log(const json& log, const string& prefix) {
        time_t now = time(nullptr);
        string filename = "logs/" + prefix + "_pricing_" + to_string(now) + ".json";
        ofstream out(filename);
        out << log.dump(2);
        out.close();
        cout << "Log saved to: " << filename << endl;
    }
};

int main() {
    DynamicPricingSimulator sim;

    cout << "Simulating weekly target: 20,000 TWD (40 hours, 150 trips):\n";
    json weekly_log = sim.simulate_orders(40, 150, 714.0);
    sim.save_log(weekly_log, "weekly");
    cout << weekly_log.dump(2) << endl;

    cout << "\nSimulating 4-day target: 12,000 TWD (32 hours, 128 trips):\n";
    json four_day_log = sim.simulate_orders(32, 128, 536.0);
    sim.save_log(four_day_log, "four_day");
    cout << four_day_log.dump(2) << endl;

    return 0;
}