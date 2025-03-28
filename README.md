# Electricity Spot Price Monitor

A Windows desktop application that monitors electricity spot prices from the PorssiSahko API and notifies users when prices exceed specified limits. Built with PyQt6, this application provides real-time monitoring and customizable notifications for electricity spot prices.

## Features

- **Real-time Price Monitoring**
  - Display of current hour's electricity spot price
  - Display of next hour's predicted price
  - Automatic updates at the start of each hour
  - Manual price refresh option

- **Customizable Notifications**
  - Set upper and lower price limits
  - Choose notification preferences:
    - Notify for lower prices
    - Notify for higher prices
    - Notify for both price conditions
  - Sound alerts using system sounds
  - Popup notifications with detailed price information

- **Price History**
  - View daily price history
  - Display prices for current and next day
  - Formatted price display with timestamps

## Requirements

- Python 3.8 or higher
- Windows operating system
- Internet connection for API access

## Dependencies

- PyQt6: For the graphical user interface
- requests: For API communication
- pytest: For running tests (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/DJeJa003/SpotPriceApp.git
cd SpotPriceApp
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

To start the application, run:
```bash
python main.py
```

## Running Tests

To run the tests, use pytest:
```bash
pytest tests/
```

## Project Structure

The project follows Clean Architecture principles for better maintainability and separation of concerns:

```
SpotPriceApp/
├── domain/           # Core business logic and entities
│   ├── entities.py   # Data models and business rules
│   └── repositories.py # Repository interfaces
├── data/            # Data access layer
│   └── api_client.py # API client implementation
├── presentation/    # UI layer
│   └── main_window.py # Main application window
├── tests/           # Test suite
├── main.py          # Application entry point
└── requirements.txt # Project dependencies
```

## Usage Guide

1. **Launch the Application**
   - Run the application using `python main.py`
   - The main window will appear with default settings

2. **Configure Price Limits**
   - Use the spin boxes to set your desired upper and lower price limits
   - Limits are in cents per kilowatt-hour (snt/kWh)

3. **Set Notification Preferences**
   - Choose when you want to receive notifications:
     - "Notify for Lower Prices": Alerts when price drops below lower limit
     - "Notify for Higher Prices": Alerts when price exceeds upper limit
     - "Notify for Both Prices": Alerts for both conditions

4. **Monitor Prices**
   - Current and next hour's prices are displayed automatically
   - Click "Update Prices" to manually refresh the data
   - Click "Show Daily Prices" to view price history

5. **Notifications**
   - When prices exceed your limits, you'll receive:
     - A system sound alert
     - A popup message with the current price
     - The notification will show whether the price is above or below your limits

## Error Handling

The application includes comprehensive error handling for various scenarios:

- **API Connection Issues**
  - Graceful handling of network errors
  - User-friendly error messages
  - Automatic retry mechanism

- **Data Validation**
  - Validation of API responses
  - Handling of missing or invalid price data
  - Proper date/time parsing

- **System Resources**
  - Graceful handling of sound playback failures
  - Memory-efficient price data management
  - Proper cleanup of system resources

## Contributing

Contributions are welcome! Please feel free to submit issues and enhancement requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Porssisahko API for providing electricity price data
- PyQt6 team for the excellent GUI framework
- All contributors who have helped improve this project 