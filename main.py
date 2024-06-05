"""This file is calculating and rendering Order Block indicator."""

from utils import *
import data_fetcher
import data_processor
import order_block_detector
import plot


df = data_fetcher.fetch_historical_data(TICKER, PERIOD)
df = data_processor.calculate_pdh_pdl(df)
sales_chart = plot.initialize_plot(df)
sales_chart = plot.add_pdh_pdl_to_plot(sales_chart, df)
df = data_processor.calculate_structure_low(df)
detector = order_block_detector.OrderBlockDetector(df)
long_order_boxes, short_order_boxes, structure_break_lines = detector.detect_order_blocks_bos()
sales_chart = plot.add_order_blocks_to_plot(
    sales_chart, df, long_order_boxes, short_order_boxes)
sales_chart = plot.add_bos_lines_to_plot(sales_chart, structure_break_lines)
sales_chart = plot.finalize_plot(sales_chart, TICKER, PERIOD)
sales_chart.show()
