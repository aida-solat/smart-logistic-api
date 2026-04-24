import React from 'react'
import Inventory from './components/Inventory'
import RouteOptimization from './components/RouteOptimization'

const App = () => {
    return (
        <div>
            <h1>Smart Logistics Dashboard</h1>
            <Inventory />
            <RouteOptimization />
        </div>
    )
}

export default App
