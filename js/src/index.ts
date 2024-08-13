import { createApp } from 'vue';

import Test from './components/Test';

const APPS = {
    chatbot: (selector: string) => {
        console.log('Loading chatbot')
        const app = createApp(Test, { message: 'yup' });
        app.mount(selector);
    }
};

export default APPS;
