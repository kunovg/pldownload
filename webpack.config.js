var path = require('path');
var webpack = require('webpack');
var BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
module.exports = {
  entry: path.resolve(__dirname, 'ReactComponents/index.js'),
  output: {
    path: path.resolve(__dirname, 'static/js'),
    filename: "bundle.js",
    publicPath: "/static/js"
  },
  stats: {
    colors: true,
    modules: true,
    reasons: true,
    errorDetails: true
  },
  module: {
    loaders: [{
      test: /\.jsx?$/,
      loader: 'babel-loader',
      query: {
        cacheDirectory: 'babel_cache',
        presets: ['react', 'es2015']
      }
    },
    { 
      test: /\.css$/, 
      loader: "style-loader!css-loader"
    }]
  },
  devtool: "#cheap-module-source-map",
  plugins: [
    // new BundleAnalyzerPlugin(),
    // new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /en|es/), // Tomar solo locale en y es de locale
    // new webpack.optimize.UglifyJsPlugin({
    //   mangle: true,
    //   compress: {
    //     warnings: false, // Suppress uglification warnings
    //     pure_getters: true,
    //     unsafe: true,
    //     unsafe_comps: true,
    //     screw_ie8: true
    //   },
    //   output: {
    //     comments: false,
    //   },
    //   exclude: [/\.min\.js$/gi] // skip pre-minified libs
    // })
  ]
}