var config = require('./webpack.config'),
    webpack = require('webpack');

config.output.filename = 'index.[chunkhash].js',
config.plugins.push(new webpack.NoEmitOnErrorsPlugin());
config.plugins.push(new webpack.DefinePlugin({'process.env': {NODE_ENV: '"production"'}}));
config.plugins.push(new webpack.optimize.MinChunkSizePlugin({minChunkSize: 100 * 1024}));
config.plugins.push(new webpack.ContextReplacementPlugin(/moment[\/\\]locale$/, /en|es/)); //Tomar solo en y es de locale

module.exports = config;