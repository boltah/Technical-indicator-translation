import utils


class OrderBlockDetector:
    """
    A class to detect order blocks and Break of Structure (BOS) lines in financial market data.

    Attributes:
        data (pd.DataFrame): The input financial market data.
        range_candle (int): The range of candles to consider for detection.
        show_bearish_bos (bool): Flag to indicate whether to show bearish BOS lines.
        show_bullish_bos (bool): Flag to indicate whether to show bullish BOS lines.
        long_boxes (list): List to store detected long order blocks.
        short_boxes (list): List to store detected short order blocks.
        bos_lines (list): List to store detected BOS lines.
        last_down_index (int): Index of the last down candle.
        last_down (float): High value of the last down candle.
        last_low (float): Low value of the last down candle.
        last_up_index (int): Index of the last up candle.
        last_long_index (int): Index of the last detected long order block.
        last_up_low (float): Low value of the last up candle.
        last_high (float): High value of the last up candle.
    """

    def __init__(self, data):
        """
        Initializes the OrderBlockDetector with the given data.

        Args:
            data (pd.DataFrame): The input financial market data.
        """
        self.data = data
        self.range_candle = utils.RANGE_CANDLE
        self.show_bearish_bos = utils.SHOW_BEARISH_BOS
        self.show_bullish_bos = utils.SHOW_BULLISH_BOS
        self.long_boxes = []
        self.short_boxes = []
        self.bos_lines = []
        self.last_down_index = self.last_down = self.last_low = 0
        self.last_up_index = self.last_long_index = self.last_up_low = self.last_high = 0

    def detect_order_blocks_bos(self):
        """
        Detects order blocks and Break of Structure (BOS) lines in the data.

        Returns:
            tuple: A tuple containing three lists:
                - long_boxes (list): Detected long order blocks.
                - short_boxes (list): Detected short order blocks.
                - bos_lines (list): Detected BOS lines.
        """
        for i in range(self.range_candle, len(self.data)):
            row = self.data.iloc[i]
            self._detect_short_boxes(row, i)
            self._detect_long_boxes(row)
            self._update_last_indices(row, i)
        return self.long_boxes, self.short_boxes, self.bos_lines

    def _detect_short_boxes(self, row, i):
        """
        Detects short order blocks in the given row of data.

        Args:
            row (pd.Series): A current row in data.
            i (int): The current index in the data.
        """
        if row["Low"] < row["StructureLow"]:
            if i - self.last_up_index < 1000:
                self.short_boxes.append(
                    (self.last_up_index, self.last_high, self.last_up_low))
                if self.show_bearish_bos:
                    candle_colour_mode = 0
                    self.bos_lines.append(
                        (self.data.index[self.last_up_index], self.last_up_low,
                         self.data.index[i], self.last_up_low, candle_colour_mode)
                    )

        for box in self.short_boxes[:]:
            if row["Close"] > box[1]:
                self.short_boxes.remove(box)
                if i - self.last_down_index < 1000 and i > self.last_long_index:
                    self.long_boxes.append(
                        (self.last_down_index, self.last_down, self.last_low))
                    if self.show_bullish_bos:
                        candle_colour_mode = 1
                        self.bos_lines.append(
                            (self.data.index[self.last_down_index], self.last_down,
                             row.name, self.last_down, candle_colour_mode)
                        )
                    self.last_long_index = i

    def _detect_long_boxes(self, row):
        """
        Detects long order blocks in the given row of data.

        Args:
            row (pd.Series): A current row in data.
        """
        for box in self.long_boxes[:]:
            if row["Close"] < box[2]:
                self.long_boxes.remove(box)

    def _update_last_indices(self, row, i):
        """
        Updates the indices and values for the last up and down candles.

        Args:
            row (pd.Series): A current row in data.
            i (int): The current index in the data.
        """
        if row["Close"] < row["Open"]:
            self.last_down = row["High"]
            self.last_down_index = i
            self.last_low = row["Low"]
        if row["Close"] > row["Open"]:
            self.last_up_index = i
            self.last_up_low = row["Low"]
            self.last_high = row["High"]
        self.last_high = max(row["High"], self.last_high)
        self.last_low = min(row["Low"], self.last_low)
