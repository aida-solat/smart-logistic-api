import React, { useState } from 'react'
import { optimizeRoute } from '../api'

const RouteOptimization = () => {
    const [route, setRoute] = useState([])
    const [start, setStart] = useState({ lat: '', lon: '' })
    const [destinations, setDestinations] = useState([{ lat: '', lon: '' }])

    const handleOptimize = () => {
        optimizeRoute({ start, destinations }).then((data) => setRoute(data.optimized_route))
    }

    return (
        <div>
            <h2>Route Optimization</h2>
            <div>
                <h4>Start Location</h4>
                <input
                    type='text'
                    placeholder='Latitude'
                    onChange={(e) => setStart({ ...start, lat: e.target.value })}
                />
                <input
                    type='text'
                    placeholder='Longitude'
                    onChange={(e) => setStart({ ...start, lon: e.target.value })}
                />
            </div>
            <div>
                <h4>Destinations</h4>
                {destinations.map((dest, idx) => (
                    <div key={idx}>
                        <input
                            type='text'
                            placeholder='Latitude'
                            onChange={(e) =>
                                setDestinations(
                                    destinations.map((d, i) => (i === idx ? { ...d, lat: e.target.value } : d)),
                                )
                            }
                        />
                        <input
                            type='text'
                            placeholder='Longitude'
                            onChange={(e) =>
                                setDestinations(
                                    destinations.map((d, i) => (i === idx ? { ...d, lon: e.target.value } : d)),
                                )
                            }
                        />
                    </div>
                ))}
            </div>
            <button onClick={handleOptimize}>Optimize Route</button>
            <div>
                <h4>Optimized Route</h4>
                <ul>
                    {route.map((r, idx) => (
                        <li key={idx}>
                            {r.lat}, {r.lon}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    )
}

export default RouteOptimization
