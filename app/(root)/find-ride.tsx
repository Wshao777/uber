import { router } from "expo-router";
import { useTranslation } from "react-i18next";
import { Text, View } from "react-native";

import CustomButton from "@/components/CustomButton";
import GoogleTextInput from "@/components/GoogleTextInput";
import RideLayout from "@/components/RideLayout";
import { icons } from "@/constants";
import { useLocationStore } from "@/store";

const FindRide = () => {
  const {
    userAddress,
    destinationAddress,
    setDestinationLocation,
    setUserLocation,
  } = useLocationStore();
  const { t } = useTranslation();

  return (
    <RideLayout title={t("findRide.title")}>
      <View className="my-3">
        <Text className="text-lg font-JakartaSemiBold mb-3">
          {t("findRide.from")}
        </Text>

        <GoogleTextInput
          icon={icons.target}
          initialLocation={userAddress!}
          containerStyle="bg-neutral-100"
          textInputBackgroundColor="#f5f5f5"
          handlePress={(location) => setUserLocation(location)}
        />
      </View>

      <View className="my-3">
        <Text className="text-lg font-JakartaSemiBold mb-3">
          {t("findRide.to")}
        </Text>

        <GoogleTextInput
          icon={icons.map}
          initialLocation={destinationAddress!}
          containerStyle="bg-neutral-100"
          textInputBackgroundColor="transparent"
          handlePress={(location) => setDestinationLocation(location)}
        />
      </View>

      <CustomButton
        title={t("findRide.button")}
        onPress={() => router.push(`/(root)/confirm-ride`)}
        className="mt-5"
      />
    </RideLayout>
  );
};

export default FindRide;
