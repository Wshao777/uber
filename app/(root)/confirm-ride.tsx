import { router } from "expo-router";
import { View, Text } from "react-native";

import CustomButton from "@/components/CustomButton";
import RideLayout from "@/components/RideLayout";

const ConfirmRide = () => {
  return (
    <RideLayout title={"Confirm your Ride"} snapPoints={["65%", "85%"]}>
        <View className="mx-5 mt-10">
            <Text className="text-lg font-JakartaSemiBold text-center">
                We are finding the best driver for you.
            </Text>
            <CustomButton
            title="Continue"
            onPress={() => router.push("/(root)/book-ride")}
            className="mt-5"
            />
        </View>
    </RideLayout>
  );
};

export default ConfirmRide;
