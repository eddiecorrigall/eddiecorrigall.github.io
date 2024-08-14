// https://webpack.js.org/guides/typescript/

const path = require('path');

module.exports = (env, argv) => {
  const mode = argv.mode || 'development'
  const isModeDevelopment = mode === 'development';

  return {
    entry: './src/index.tsx',
    // https://webpack.js.org/configuration/devtool/
    devtool: isModeDevelopment ? 'eval' : false,
    devServer: {
      static: './dist',
    },
    mode: 'development',
    module: {
      rules: [
        {
          test: /\.tsx?$/,
          use: 'ts-loader',
          exclude: /node_modules/,
        },
      ],
    },
    performance: {
      hints: isModeDevelopment ? false : 'error',
    },
    resolve: {
      extensions: ['.tsx', '.ts', '.js'],
    },
    output: {
      library: 'MyApps',
      libraryTarget: 'umd',
      libraryExport: 'default',
      filename: 'bundle.js',
      path: path.resolve(__dirname, 'dist'),
    },
  };
};
