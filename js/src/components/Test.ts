import { defineComponent } from 'vue'

export default defineComponent({
    // type inference enabled
    props: {
        message: String
    },
    setup(props) {
        props.message // type: string | undefined
    },
    render() {
        return `This is a message: ${this.$props.message}`;
    }
})
