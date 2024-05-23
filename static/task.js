const { createApp } = Vue
const TaskApp = {
    data() {
        return {
            selectedTask: null,
            scrollWidth: 0,
            isDisabled: true,
            task: {
                'id': '',
                'title': '',
                'date': '',
                'completed': '',
                'drone_id': '',
                'drone_name': '',
                'drone_connected': '',
            },
            tasks: []
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
        await this.getTasks();
    },
    methods: {
        calculateScrollWidth() {
          const tableContentWidth = this.$refs["tbl-content"].offsetWidth;
          const tableWidth = this.$refs["tbl-content"].querySelector('table').offsetWidth;
          this.scrollWidth = tableContentWidth - tableWidth;
        },
        selectRow(task) {
            this.selectedTask = task
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
        async getTasks() {
            const response = await this.sendRequest(window.location, 'get')
            this.tasks = await response.json()
        },
        async createTask() {
            await this.getTasks()
            const response = await this.sendRequest(window.location, 'post', JSON.stringify(this.task))
            await this.getTasks()
            this.task.id = ''
            this.task.title = ''
            this.task.date = ''
            this.task.completed = ''
            this.task.drone_id = ''
            this.task.drone_name = ''
            this.task.drone_connected = ''
        },
        async createTask() {
            await this.getTasks()
            const response = await this.sendRequest(window.location, 'post', JSON.stringify(this.task))
            await this.getTasks()
            this.task.id = ''
            this.task.title = ''
            this.task.date = ''
            this.task.completed = ''
            this.task.drone_id = ''
            this.task.drone_name = ''
            this.task.drone_connected = ''
        },
        async deleteTask() {
            await this.sendRequest(window.location + "/" + this.selectedTask, 'delete')
            await this.getTasks()
        },
        async updateTask() {
            await this.getTasks()
            const response = await this.sendRequest(window.location + "/" + this.selectedTask, 'put', JSON.stringify(this.task))
            await this.getTasks()
            this.selectedTask = null
        },
        async getTask() {
            const response = await this.sendRequest(window.location + "/" + this.selectedTask, 'get')
            this.tasks = await response.json()
        },
        async executeTask(task) {
            await this.sendRequest(window.location + "/" + this.selectedTask + '/execute', 'post', JSON.stringify(task))
            await this.getTasks()
        },
        showImages(task) {
            window.location.href = '/api/tasks/' + this.selectedTask + '/images'
        }
    },
    delimiters: ['{', '}']
}

createApp(TaskApp).mount('#appTask');