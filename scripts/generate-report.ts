import { neon } from "@neondatabase/serverless";
import * as dotenv from "dotenv";
import * as fs from "fs";
import * as csv from "fast-csv";
import path from "path";
import { Goddess, Ride } from "@/types/type";

dotenv.config();

const generateReport = async () => {
  try {
    const sql = neon(process.env.DATABASE_URL!);
    const rides: Ride[] = await sql`SELECT * FROM rides`;

    const goddesses: Goddess[] = JSON.parse(
      fs.readFileSync(path.resolve(__dirname, "../lib/goddess_truecodes.json"), "utf-8")
    );

    const goddessMap = new Map(goddesses.map((g) => [g.id, g.name]));

    const reportData = rides.map((ride) => ({
      ...ride,
      goddess_name: goddessMap.get(ride.driver_id) || "Unknown",
    }));

    const ws = fs.createWriteStream("daily_report.csv");
    csv
      .write(reportData, { headers: true })
      .on("finish", function () {
        console.log("CSV report generated successfully.");
      })
      .pipe(ws);
  } catch (error) {
    console.error("Error generating report:", error);
  }
};

generateReport();
