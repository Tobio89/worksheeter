console.log('WSM_VUE FILE WAS LOADED')
console.log('WE GON MAKE THIS SITE VUETIFUL well a little anyway')


let sheet_instructions = new Vue({
    el: '#instructions',
    delimiters: ['%[', ']%'],
    data: {
        show_instructions:false,
        main_shown:false,
        read_shown:false,
        list_shown:false,
    },
    methods:{},
    computed:{
        instructions_title: function() {
            if (this.show_instructions){
                return 'How To Use Auto Worksheet'
            } else {
                return 'Would You Like To Know More?'
            }
        }
    }
})

let form_mode = new Vue({
    el: '#form_selection',
    delimiters: ['%[', ']%'],
    data: {
        article_mode:true,
        custom_mode:false,
    },
    methods:{
        turn_on_article_mode: function() {
            console.log('Article select')
            this.article_mode = true;
            this.custom_mode = false;
        },
        turn_on_custom_mode: function() {
            console.log('Text entry')
            this.article_mode = false;
            this.custom_mode = true;
        },

    } 



})
