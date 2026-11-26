from typing import List
from .base import BaseTemplate

class ExpoMobileTemplate(BaseTemplate):
    id = "expo_mobile"
    name = "Mobile App (React Native / Expo + TypeScript)"
    short_name = "Mobile App (React Native / Expo)"
    description = "Cross-platform mobile application powered by Expo SDK, React Native, and TypeScript."
    category = "Mobile"
    has_node = True
    has_python = False

    def scaffold(self) -> List[str]:
        files_created = []

        # package.json
        pkg_json = """{
  "name": "{{PROJECT_NAME_LOWER}}",
  "version": "1.0.0",
  "scripts": {
    "start": "expo start",
    "android": "expo start --android",
    "ios": "expo start --ios",
    "web": "expo start --web"
  },
  "dependencies": {
    "expo": "~51.0.0",
    "expo-status-bar": "~1.12.1",
    "react": "18.2.0",
    "react-native": "0.74.5"
  },
  "devDependencies": {
    "@babel/core": "^7.20.0",
    "@types/react": "~18.2.45",
    "typescript": "~5.3.3"
  },
  "private": true
}"""
        self.write_file("package.json", pkg_json)
        files_created.append("package.json")

        # app.json
        app_json = """{
  "expo": {
    "name": "{{PROJECT_NAME}}",
    "slug": "{{PROJECT_NAME_LOWER}}",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "userInterfaceStyle": "light",
    "splash": {
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "ios": {
      "supportsTablet": true
    },
    "android": {
      "adaptiveIcon": {
        "backgroundColor": "#ffffff"
      }
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  }
}"""
        self.write_file("app.json", app_json)
        files_created.append("app.json")

        # tsconfig.json
        self.write_file("tsconfig.json", """{
  "extends": "expo/tsconfig.base",
  "compilerOptions": {
    "strict": true
  }
}""")
        files_created.append("tsconfig.json")

        # babel.config.js
        self.write_file("babel.config.js", """module.exports = function(api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
  };
};
""")
        files_created.append("babel.config.js")

        # App.tsx
        app_tsx = """import { StatusBar } from 'expo-status-bar';
import { StyleSheet, Text, View } from 'react-native';

export default function App() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{{PROJECT_NAME}}</Text>
      <Text style={styles.subtitle}>Scaffolded with Aayush's DevKit</Text>
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#38bdf8',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#94a3b8',
  },
});
"""
        self.write_file("App.tsx", app_tsx)
        files_created.append("App.tsx")

        return files_created
