// https://webpack.js.org/guides/typescript/

const path = require('path')

const MiniCssExtractPlugin = require('mini-css-extract-plugin')

module.exports = (env, argv) => {
  const mode = argv.mode || 'development'
  const isModeProduction = mode === 'production'

  return {
    entry: './src/index.tsx',
    // https://webpack.js.org/configuration/devtool/
    devtool: isModeProduction ? false : 'inline-source-map',
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
        {
          test: /\.css$/,
          use: [
            isModeProduction ? MiniCssExtractPlugin.loader : 'style-loader',
            {
              loader: 'css-loader',
              options: {
                modules: true,
              },
            },
          ],
        },
      ],
    },
    plugins: [
      new MiniCssExtractPlugin(),
    ],
    performance: {
      hints: isModeProduction ? 'error' : false,
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
  }
}
