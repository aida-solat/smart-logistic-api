import React, { useEffect, useState } from "react";
import { fetchInventory } from "../api";

const Inventory = () => {
    const [inventory, setInventory] = useState([]);

    useEffect(() => {
        fetchInventory().then(data => setInventory(data));
    }, []);

    return (
        <div>
            <h2>Inventory</h2>
            <ul>
                {inventory.map(item => (
                    <li key={item.id}>
                        {item.item_name} - {item.stock} units ({item.location})
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Inventory;
