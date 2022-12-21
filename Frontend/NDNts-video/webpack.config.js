const path = require("path");

/** @return {import("webpack").Configuration} */
module.exports = (env, argv) => ({
  // mode: argv.mode ?? "production",
  mode: "production",
  devtool: argv.mode === "development" ? "cheap-module-source-map" : "source-map",
  entry: "./src/main.jsx",
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env"],
            plugins: [
              "babel-plugin-transform-redom-jsx",
              [
                "transform-react-jsx",
                {
                  pragma: "el",
                },
              ],
            ],
          },
        },
      },
    ],
  },
  resolve: {
    extensions: [".jsx", ".js"],
  },
  output: {
    filename: "bundle.js",
    path: path.resolve(__dirname, "public"),
  },
  node: false,
  devServer: {
    // contentBase: path.resolve(__dirname, "public"),
    // disableHostCheck: true,
    port: 3333,
  },
  performance: {
    hints: false,
    maxEntrypointSize: 512000,
    maxAssetSize: 512000
  }
});
