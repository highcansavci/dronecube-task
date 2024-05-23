const { createApp } = Vue
const DroneApp = {
    data() {
        return {
            selectedDrone: null,
            scrollWidth: 0,
            isDisabled: true,
            drone: {
                'id': '',
                'name': '',
                'latitude': '',
                'longitude': '',
                'altitude': '',
                'home_latitude': '',
                'home_longitude': '',
                'home_altitude': '',
                'velocity_x': '',
                'velocity_y': '',
                'velocity_z': '',
                'connected': '',
            },
            drones: [],
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
        await this.getDrones();
    },
    methods: {
        calculateScrollWidth() {
          const tableContentWidth = this.$refs["tbl-content"].offsetWidth;
          const tableWidth = this.$refs["tbl-content"].querySelector('table').offsetWidth;
          this.scrollWidth = tableContentWidth - tableWidth;
        },
        selectRow(drone) {
            this.selectedDrone = drone
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
            const response = await this.sendRequest("/api/tasks", 'get')
            this.tasks = await response.json()
        },
        async createTask(drone_id) {
            await this.getTasks()
            this.task.drone_id = drone_id
            const response = await this.sendRequest("/api/tasks", 'post', JSON.stringify(this.task))
            await this.getTasks()
            this.task.id = ''
            this.task.title = ''
            this.task.date = ''
            this.task.completed = ''
            this.task.drone_id = ''
            this.task.drone_name = ''
            this.task.drone_connected = ''
        },
        async getDrones() {
            const response = await this.sendRequest(window.location, 'get')
            this.drones = await response.json()
        },
        async createDrone() {
            await this.getDrones()
            const response = await this.sendRequest(window.location, 'post', JSON.stringify(this.drone))
            await this.getDrones()
            this.drone.id = ''
            this.drone.name = ''
            this.drone.latitude = ''
            this.drone.longitude = ''
            this.drone.altitude = ''
            this.drone.home_latitude = ''
            this.drone.home_longitude = ''
            this.drone.home_altitude = ''
            this.drone.velocity_x = ''
            this.drone.velocity_y = ''
            this.drone.velocity_z = ''
            this.drone.connected = ''
        },
        async deleteDrone() {
            await this.sendRequest(window.location + "/" + this.selectedDrone, 'delete')
            await this.getDrones()
        },
        async updateDrone() {
            await this.getDrones()
            const response = await this.sendRequest(window.location + "/" + this.selectedDrone, 'put', JSON.stringify(this.drone))
            await this.getDrones()
            this.selectedDrone = null
        },
        async getDrone() {
            const response = await this.sendRequest(window.location + "/" + this.selectedDrone, 'get')
            this.drones = await response.json()
        }
    },
    delimiters: ['{', '}']
}

createApp(DroneApp).mount('#appDrone');
