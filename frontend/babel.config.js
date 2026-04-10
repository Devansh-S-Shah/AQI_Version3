module.exports = function (api) {
  api.cache(true);
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      'react-native-worklets/plugin', // Required by react-native-reanimated 4.x — must be last
    ],
  };
};
