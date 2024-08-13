// https://webpack.js.org/guides/typescript/

const path = require('path');

module.exports = {
    entry: './src/index.ts',
    mode: 'development',
    performance: {
        hints: 'error'
    },
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ],
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
    }
};
