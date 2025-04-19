import React, { useState, useEffect } from "react";
import axios from "axios";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import "./predictions.css";

const Predictions = () => {
  const [predictedSales, setPredictedSales] = useState([]);
  const [predictedStock, setPredictedStock] = useState([]);
  const [loading, setLoading] = useState(false);
  const [invStartDate, setInvStartDate] = useState(new Date());
  const [invEndDate, setInvEndDate] = useState(new Date(new Date().setDate(new Date().getDate() + 6)));

  // State to track which table is displayed
  const [showInventory, setShowInventory] = useState(false);

  useEffect(() => {
    fetchSalesPredictions(); // Load sales predictions on page load
  }, []);

  const fetchSalesPredictions = async () => {
    try {
      setLoading(true);
      const salesResponse = await axios.get("http://127.0.0.1:5000/predict-sales");
      setPredictedSales(salesResponse.data);
    } catch (error) {
      console.error("Error fetching sales predictions:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchInventoryPredictions = async () => {
    try {
      setLoading(true);
      const stockResponse = await axios.get("http://127.0.0.1:5000/predict-inventory", {
        params: {
          start_date: invStartDate.toISOString().split("T")[0],
          end_date: invEndDate.toISOString().split("T")[0],
        },
      });
      setPredictedStock(stockResponse.data.filter(stock => stock.predicted_quantity > 0)); // Remove 0 predictions
    } catch (error) {
      console.error("Error fetching inventory predictions:", error);
    } finally {
      setLoading(false);
    }
  };

  // Function to switch tables
  const toggleTable = () => {
    if (showInventory) {
      fetchSalesPredictions();
    } else {
      fetchInventoryPredictions();
    }
    setShowInventory(!showInventory);
  };

  // Utility function to group predictions by date
  const groupByDate = (data, dateField = "date") => {
    return data.reduce((groups, item) => {
      const date = item[dateField];
      if (!groups[date]) {
        groups[date] = [];
      }
      groups[date].push(item);
      return groups;
    }, {});
  };

  return (
    <div className="predictions-container">
      <div className="head">
        <h1>PREDICTIONS</h1>

        <button className="toggle-btn" onClick={toggleTable}>
          {showInventory ? "Show Sales Predictions" : "Show Inventory Predictions"}
        </button>
      </div>

      {/* Sales Predictions Table (Default) */}
      {!showInventory && (
        <>
          <h2>Predicted Sales</h2>
          <div className="table-container">
            <table className="prediction-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Item Name</th>
                  <th>Predicted Sales</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(groupByDate(predictedSales)).map(([date, items]) => (
                  <React.Fragment key={date}>
                    <tr className="date-group"><td colSpan="3"><strong>{date}</strong></td></tr>
                    {items.map((sale, index) => (
                      <tr key={index}><td></td><td>{sale.item_name}</td><td>{sale.predicted_sales}</td></tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Inventory Predictions Table */}
      {showInventory && (
        <>
          {/* Date Range Picker */}
          <div className="datepicker-container">
            <label>Select Inventory Date Range: </label>
            <DatePicker
              selected={invStartDate}
              onChange={([start, end]) => {
                setInvStartDate(start);
                setInvEndDate(end || new Date(start.getTime() + 6 * 24 * 60 * 60 * 1000)); // fallback if end not chosen
                  }}
              selectsRange
              startDate={invStartDate}
              endDate={invEndDate}
              dateFormat="yyyy-MM-dd"
            />
          </div>

          <h2>Predicted Inventory</h2>
          <div className="table-container">
            <table className="prediction-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Product</th>
                  <th>Predicted Stock Usage</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(groupByDate(predictedStock)).map(([date, items]) => (
                  <React.Fragment key={date}>
                    <tr className="date-group"><td colSpan="3"><strong>{date}</strong></td></tr>
                    {items.map((stock, index) => (
                      <tr key={index}><td></td><td>{stock.product}</td><td>{stock.predicted_quantity}</td></tr>
                    ))}
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {loading && <p>Loading predictions...</p>}
    </div>
  );
};

export default Predictions;
