# Electricity Spot Price Monitor

A Windows desktop application that monitors electricity spot prices from the PorssiSahko API and notifies users when prices exceed specified limits.

## Features

- Real-time monitoring of electricity spot prices
- Display of current and next hour's prices
- Customizable price limits with notifications
- Sound and popup notifications when prices exceed limits
- Automatic updates every minute

## Requirements

- Python 3.8 or higher
- Windows operating system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/SpotPriceApp.git
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

The project follows Clean Architecture principles:

- `domain/`: Core business logic and entities
- `data/`: Data access and API integration
- `presentation/`: UI components
- `tests/`: Test suite

## Usage

1. Launch the application
2. Set your desired price limits using the spin boxes
3. The application will automatically fetch and display current prices
4. When prices exceed your limits, you'll receive both a sound and popup notification
5. Click the "Update Prices" button to manually refresh the prices

## Error Handling

The application handles various error cases:
- API connection issues
- Invalid data formats
- Missing price data
- Sound file not found

## Contributing

Feel free to submit issues and enhancement requests! 