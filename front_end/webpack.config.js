const webpack = require("webpack");
const path = require("path");

const config = {
  entry: "./src/index.js",

  output: {
    path: path.resolve(__dirname, "dist"),
    filename: "app.js",
    publicPath: '',
  },
  plugins: [
    new webpack.ProvidePlugin({
      process: "process/browser",
    }),
    new webpack.ProvidePlugin({
      Buffer: ["buffer", "Buffer"],
    })
  ],
  module: {
    rules: [
        {
            test: /\.(m?js)$/,
            type: "javascript/auto",
          },
          {
            test: /\.(m?js)$/,
            resolve: {
              fullySpecified: false,
            },
          },
    ]
  },
  resolve: {
    extensions: [".ts", ".js"],
    fallback: {
      buffer: require.resolve("buffer/"),
      os: require.resolve("os-browserify"),
      path: require.resolve("path-browserify"),
      process: require.resolve('process/browser'),
      crypto: require.resolve('crypto-browserify'),
      stream: require.resolve("stream-browserify"),
      vm: require.resolve("vm-browserify")
    },
  },
};

module.exports = config;