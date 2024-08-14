// https://webpack.js.org/guides/typescript/
// https://vue-loader.vuejs.org/guide/#manual-setup

const path = require('path');
const { VueLoaderPlugin } = require('vue-loader');

module.exports = {
    entry: './src/index.ts',
    mode: 'production',
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
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.css$/i,
                loader: "css-loader",
            },
        ],
    },
    plugins: [
        new VueLoaderPlugin(),
    ],
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
