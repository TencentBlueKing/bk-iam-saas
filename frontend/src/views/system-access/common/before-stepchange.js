export default {
    data () {
        return {
            routerName: { 1: 'systemAccessAccess', 2: 'systemAccessRegistry', 3: 'systemAccessOptimize', 4: 'systemAccessComplete' }
        }
    },
    methods: {
        async beforeStepChanged (index) {
            const modelingId = this.$route.params.id
            if (modelingId) {
                if (this.controllableSteps.curStep === 4) {
                    this.$nextTick(() => {
                        this.$router.push({
                            name: this.routerName[index],
                            params: {
                                id: modelingId
                            }
                        })
                    })
                } else {
                    this.handleSubmit(this.routerName[index])
                }
            }
        }
    }
}
