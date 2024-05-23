const { createApp } = Vue
const ImageApp = {
    data() {
        return {
            selectedImage: null,
            url: null,
            filename: null,
            scrollWidth: 0,
            isDisabled: true,
            image: {
                'id': '',
                'date': '',
                'filename': '',
                'task_id': '',
                'task_title': '',
                'task_date': '',
                'task_completed': '',
            },
            images: []
        }
    },
    mounted() {
        this.calculateScrollWidth();
        window.addEventListener('resize', this.calculateScrollWidth);
    },
    beforeDestroy() {
        window.removeEventListener('resize', this.calculateScrollWidth);
    },
    async created() {
        await this.getImages();
    },
    methods: {
        calculateScrollWidth() {
          const tableContentWidth = this.$refs["tbl-content"].offsetWidth;
          const tableWidth = this.$refs["tbl-content"].querySelector('table').offsetWidth;
          this.scrollWidth = tableContentWidth - tableWidth;
        },
        selectRow(image) {
            this.selectedImage = image
            this.isDisabled = false
        },
        async sendRequest(url, method, data) {
            const myHeaders = new Headers({
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            })
            const response = await fetch(url, {
                method: method,
                headers: myHeaders,
                body: data
            })
            return response
        },
        async getImages() {
            const response = await this.sendRequest(window.location + "/view", 'get')
            this.images = await response.json()
        },
        async getImage() {
            const response = await this.sendRequest(window.location + "/view/" + this.selectedImage, 'get')
            const response_json = await response.json()
            this.url = response_json.url
            this.filename = response_json.filename
        }
    },
    delimiters: ['{', '}']
}

createApp(ImageApp).mount('#appImage');