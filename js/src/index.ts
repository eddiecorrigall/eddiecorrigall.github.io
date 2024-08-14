import { createApp } from 'vue';

import HelloWorld from './components/HelloWorld.vue';

const APPS = {
    chatbot: (options: { api: string, selector: string }) => {
        const { api, selector } = options;
        console.log('Loading chatbot')
        const app = createApp(HelloWorld);
        app.mount(selector);
    }
};

export default APPS;
