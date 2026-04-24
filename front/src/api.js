import axios from 'axios'

const API_URL = 'http://<your-api-url>'

export const fetchInventory = async () => {
    const response = await axios.get(`${API_URL}/inventory`)
    return response.data
}

export const optimizeRoute = async (routeRequest) => {
    const response = await axios.post(`${API_URL}/optimize-route`, routeRequest)
    return response.data
}
