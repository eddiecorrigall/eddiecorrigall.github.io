import { createApp } from 'vue';

import Test from './components/Test';

const APPS = {
    chatbot: (options: { api: string, selector: string }) => {
        const { api, selector } = options;
        console.log('Loading chatbot')
        const app = createApp(Test, { message: 'yup' });
        app.mount(selector);
    }
};

export default APPS;
