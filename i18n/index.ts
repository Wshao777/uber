import i18next from "i18next";
import { initReactI18next } from "react-i18next";
import * as Localization from "expo-localization";

import en from "./locales/en/translation.json";
import zh from "./locales/zh/translation.json";

const resources = {
  en: {
    translation: en,
  },
  zh: {
    translation: zh,
  },
};

i18next.use(initReactI18next).init(
  {
    resources,
    lng: Localization.locale,
    fallbackLng: "en",
    interpolation: {
      escapeValue: false,
    },
  },
  () => {
    console.log("i18n initialized, language:", i18next.language);
  },
);

export default i18next;
