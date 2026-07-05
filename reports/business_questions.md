
# Trả lời câu hỏi kinh doanh

## A. Hiệu quả điều hành

**A1. Doanh thu, lợi nhuận và weighted margin biến động thế nào theo tháng, quý, năm?**  
Bảng tháng, quý và năm đã được xuất tại `reports/tables/monthly_performance.csv`, `quarterly_performance.csv`, và `yearly_performance.csv`. Năm 2017 đạt doanh thu $215,387.27, nhưng margin chỉ 1.40%.  
**Hàm ý:** tăng trưởng doanh thu cần được quản trị cùng chất lượng lợi nhuận, không chỉ theo doanh số.

| order_year | total_sales | total_profit | profit_margin | sales_growth | profit_growth |
| --- | --- | --- | --- | --- | --- |
| 2014.0 | $157,192.85 | $5,457.73 | 3.47% | N/A | N/A |
| 2015.0 | $170,518.24 | $3,015.20 | 1.77% | 8.48% | -44.75% |
| 2016.0 | $198,901.44 | $6,959.95 | 3.50% | 16.65% | 130.83% |
| 2017.0 | $215,387.27 | $3,018.39 | 1.40% | 8.29% | -56.63% |

| order_quarter | total_sales | total_profit | profit_margin | sales_growth | profit_growth |
| --- | --- | --- | --- | --- | --- |
| 2014-Q1 | $22,656.14 | $-202.50 | -0.89% | N/A | N/A |
| 2014-Q2 | $28,063.75 | $800.82 | 2.85% | 23.87% | 495.47% |
| 2014-Q3 | $41,957.88 | $2,896.32 | 6.90% | 49.51% | 261.67% |
| 2014-Q4 | $64,515.09 | $1,963.09 | 3.04% | 53.76% | -32.22% |
| 2015-Q1 | $27,374.10 | $-1,164.25 | -4.25% | -57.57% | -159.31% |
| 2015-Q2 | $27,564.83 | $826.58 | 3.00% | 0.70% | 171.00% |
| 2015-Q3 | $49,586.04 | $537.55 | 1.08% | 79.89% | -34.97% |
| 2015-Q4 | $65,993.28 | $2,815.32 | 4.27% | 33.09% | 423.73% |

**A2-A3. Tăng trưởng doanh thu có chuyển thành tăng trưởng lợi nhuận không, và kỳ nào lệch nhất?**  
Các kỳ dưới đây có doanh thu xếp hạng cao hơn nhiều so với lợi nhuận.  
**Hàm ý:** cần review khuyến mại, nhóm sản phẩm và bang trong các kỳ doanh thu cao nhưng profit yếu.

| order_month_label | total_sales | total_profit | profit_margin | sales_rank | profit_rank | divergence_score |
| --- | --- | --- | --- | --- | --- | --- |
| 2017-10 | $21,884.07 | $-2,526.92 | -11.55% | 12 | 47 | 35 |
| 2014-03 | $14,573.96 | $-1,128.65 | -7.74% | 18 | 46 | 28 |
| 2014-11 | $21,564.87 | $-297.90 | -1.38% | 13 | 38 | 25 |
| 2017-11 | $37,056.72 | $406.06 | 1.10% | 1 | 21 | 20 |
| 2015-07 | $13,674.42 | $-325.09 | -2.38% | 19 | 39 | 20 |
| 2016-03 | $12,801.09 | $-555.27 | -4.34% | 24 | 44 | 20 |
| 2017-05 | $16,957.56 | $-72.88 | -0.43% | 15 | 34 | 19 |
| 2016-08 | $12,483.23 | $-494.15 | -3.96% | 26 | 43 | 17 |

**A4. Tỷ lệ dòng giao dịch bị lỗ là bao nhiêu?**  
Có 714 dòng lỗ, tương đương 33.66% tổng số dòng.  
**Hàm ý:** lỗ không phải ngoại lệ nhỏ; cần worklist kiểm soát giá/discount ở cấp dòng.

## B. Sản phẩm và danh mục

**B1. Sub-category nào tạo doanh thu, lợi nhuận và margin?**  
**Hàm ý:** Chairs tạo profit lớn nhất, Furnishings có margin tốt nhất; Tables và Bookcases cần sửa lợi nhuận trước khi mở rộng.

| sub_category | total_sales | total_profit | profit_margin | loss_line_rate |
| --- | --- | --- | --- | --- |
| Chairs | $328,449.10 | $26,590.17 | 8.10% | 38.09% |
| Tables | $206,965.53 | $-17,725.48 | -8.56% | 63.64% |
| Bookcases | $114,880.00 | $-3,472.56 | -3.02% | 47.81% |
| Furnishings | $91,705.16 | $13,059.14 | 14.24% | 17.45% |

**B2. Sản phẩm nào doanh thu cao nhưng lợi nhuận thấp hoặc âm?**  
**Hàm ý:** các sản phẩm này thuộc nhóm `Repair`: cần xem lại giá, mức giảm giá và vùng bán.

| product_id | product_name | sub_category | total_sales | total_profit | profit_margin | classification |
| --- | --- | --- | --- | --- | --- | --- |
| FUR-CH-10002024 | HON 5400 Series Task Chairs for Big and Tall | Chairs | $21,870.58 | $0.00 | 0.00% | Repair |
| FUR-BO-10004834 | Riverside Palais Royal Lawyers Bookcase, Royale Cherry Finish | Bookcases | $15,610.97 | $-669.54 | -4.29% | Repair |
| FUR-TA-10003473 | Bretford Rectangular Conference Table Tops | Tables | $12,995.29 | $-327.23 | -2.52% | Repair |
| FUR-BO-10002213 | DMI Eclipse Executive Suite Bookcases | Bookcases | $11,046.61 | $90.18 | 0.82% | Repair |
| FUR-TA-10000198 | Chromcraft Bull-Nose Wood Oval Conference Tables & Bases | Tables | $9,917.64 | $-2,876.12 | -29.00% | Repair |
| FUR-TA-10001889 | Bush Advantage Collection Racetrack Conference Table | Tables | $9,544.73 | $-1,934.40 | -20.27% | Repair |
| FUR-TA-10001095 | Chromcraft Round Conference Tables | Tables | $8,209.06 | $-189.98 | -2.31% | Repair |
| FUR-TA-10003954 | Hon 94000 Series Round Tables | Tables | $7,404.50 | $-681.21 | -9.20% | Repair |
| FUR-TA-10000577 | Bretford CR4500 Series Slim Rectangular Table | Tables | $7,242.77 | $-532.76 | -7.36% | Repair |
| FUR-TA-10002958 | Bevis Oval Conference Table, Walnut | Tables | $6,942.07 | $-856.01 | -12.33% | Repair |

**B3. Sản phẩm nào có lợi nhuận tốt nhưng chưa đại diện lớn trong doanh thu?**  
**Hàm ý:** đây là nhóm có thể scale/cross-sell chọn lọc thay vì giảm giá đại trà.

| product_id | product_name | sub_category | total_sales | total_profit | profit_margin |
| --- | --- | --- | --- | --- | --- |
| FUR-FU-10002937 | GE 48" Fluorescent Tube, Cool White Energy Saver, 34 Watts, 30/Box | Furnishings | $2,699.06 | $1,260.22 | 46.69% |
| FUR-FU-10002671 | Electrix 20W Halogen Replacement Bulb for Zoom-In Desk Lamp | Furnishings | $168.84 | $78.26 | 46.35% |
| FUR-FU-10001861 | Floodlight Indoor Halogen Bulbs, 1 Bulb per Pack, 60 Watts | Furnishings | $434.56 | $197.10 | 45.36% |
| FUR-FU-10002045 | Executive Impressions 14" | Furnishings | $377.91 | $166.28 | 44.00% |
| FUR-FU-10000409 | GE 4 Foot Flourescent Tube, 40 Watt | Furnishings | $98.87 | $42.24 | 42.73% |
| FUR-FU-10003274 | Regeneration Desk Collection | Furnishings | $35.90 | $15.21 | 42.35% |
| FUR-FU-10000771 | Eldon 200 Class Desk Accessories, Smoke | Furnishings | $138.16 | $58.03 | 42.00% |
| FUR-FU-10002597 | C-Line Magnetic Cubicle Keepers, Clear Polypropylene | Furnishings | $136.34 | $56.12 | 41.16% |
| FUR-FU-10000629 | 9-3/4 Diameter Round Wall Clock | Furnishings | $455.07 | $183.13 | 40.24% |
| FUR-FU-10001591 | Advantus Panel Wall Certificate Holder - 8.5x11 | Furnishings | $270.84 | $108.09 | 39.91% |

**B4-B5. Sản phẩm/sub-category và tổ hợp region x sub-category nào lỗ lớn nhất?**  
**Hàm ý:** ưu tiên review top loss products và ô region x sub-category âm sâu trước.

| product_id | product_name | sub_category | total_sales | total_profit | profit_margin |
| --- | --- | --- | --- | --- | --- |
| FUR-TA-10000198 | Chromcraft Bull-Nose Wood Oval Conference Tables & Bases | Tables | $9,917.64 | $-2,876.12 | -29.00% |
| FUR-TA-10001889 | Bush Advantage Collection Racetrack Conference Table | Tables | $9,544.73 | $-1,934.40 | -20.27% |
| FUR-TA-10001950 | Balt Solid Wood Round Tables | Tables | $6,518.75 | $-1,201.06 | -18.42% |
| FUR-TA-10004289 | BoxOffice By Design Rectangular and Half-Moon Meeting Room Tables | Tables | $1,706.25 | $-1,148.44 | -67.31% |
| FUR-TA-10004154 | Riverside Furniture Oval Coffee Table, Oval End Table, End Table with Drawer | Tables | $4,446.18 | $-1,147.40 | -25.81% |
| FUR-CH-10003312 | Hon 2090 ÒPillow SoftÓ Series Mid Back Swivel/Tilt Chairs | Chairs | $5,282.42 | $-989.05 | -18.72% |
| FUR-BO-10001972 | O'Sullivan 4-Shelf Bookcase in Odessa Pine | Bookcases | $2,740.20 | $-975.10 | -35.58% |
| FUR-TA-10004256 | Bretford ÒJust In TimeÓ Height-Adjustable Multi-Task Work Tables | Tables | $5,634.90 | $-964.19 | -17.11% |
| FUR-TA-10002958 | Bevis Oval Conference Table, Walnut | Tables | $6,942.07 | $-856.01 | -12.33% |
| FUR-TA-10002533 | BPI Conference Tables | Tables | $2,241.87 | $-795.97 | -35.50% |

| region | sub_category | total_sales | total_profit | profit_margin | average_discount | loss_line_rate |
| --- | --- | --- | --- | --- | --- | --- |
| East | Tables | $39,139.81 | $-11,025.38 | -28.17% | 37.37% | 97.50% |
| South | Tables | $43,916.19 | $-4,623.06 | -10.53% | 22.25% | 52.94% |
| Central | Furnishings | $15,254.37 | $-3,906.22 | -25.61% | 40.39% | 67.32% |
| Central | Tables | $39,154.97 | $-3,559.65 | -9.09% | 26.25% | 68.06% |
| Central | Bookcases | $24,157.18 | $-1,997.90 | -8.27% | 23.28% | 72.00% |
| West | Bookcases | $36,004.12 | $-1,646.51 | -4.57% | 22.87% | 40.00% |
| East | Bookcases | $43,819.33 | $-1,167.63 | -2.66% | 22.00% | 47.14% |
| South | Bookcases | $10,899.36 | $1,339.49 | 12.29% | 10.00% | 28.57% |
| West | Tables | $84,754.56 | $1,482.61 | 1.75% | 20.00% | 42.24% |
| South | Furnishings | $17,306.68 | $3,442.68 | 19.89% | 10.67% | 4.24% |

## C. Rủi ro discount và pricing

**C1. Profit và loss rate khác nhau thế nào theo discount level/band?**  
**Hàm ý:** discount càng cao càng cần kiểm soát margin; band `>30%` là vùng rủi ro rõ rệt.

| discount_band | total_sales | total_profit | profit_margin | loss_line_rate |
| --- | --- | --- | --- | --- |
| 0% | $256,025.27 | $58,133.08 | 22.71% | 0.00% |
| 1-10% | $46,634.25 | $7,111.01 | 15.25% | 5.26% |
| 11-20% | $244,189.54 | $7,684.94 | 3.15% | 27.44% |
| 21-30% | $99,470.35 | $-10,695.32 | -10.75% | 93.24% |
| >30% | $95,680.39 | $-43,782.44 | -45.76% | 100.00% |

**C2. Ngưỡng discount đầu tiên có aggregate profit âm là gì?**  
Discount 30.00% là mức đầu tiên có tổng profit âm trong bảng exact discount, với profit $-10,695.32. Nhóm discount >=30% có profit $-54,477.76 và loss-line rate 97.23%.  
**Hàm ý:** discount >=30% nên là exception cần phê duyệt margin.

**C3. Nhóm nào phơi nhiễm discount cao nhất?**  
**Hàm ý:** ưu tiên review các tổ hợp sub-category x region và state có profit âm dưới ngưỡng >=30%.

| sub_category | region | total_sales | total_profit | average_discount | loss_line_rate |
| --- | --- | --- | --- | --- | --- |
| Tables | East | $39,139.81 | $-11,025.38 | 37.37% | 97.50% |
| Tables | South | $21,381.06 | $-8,840.78 | 42.04% | 100.00% |
| Tables | Central | $22,311.33 | $-6,526.42 | 37.06% | 96.08% |
| Furnishings | Central | $6,644.70 | $-5,944.66 | 60.00% | 100.00% |
| Tables | West | $7,124.34 | $-4,305.64 | 50.00% | 100.00% |
| Bookcases | East | $7,308.46 | $-4,255.81 | 50.00% | 100.00% |
| Chairs | Central | $41,135.63 | $-4,094.34 | 30.00% | 94.95% |
| Bookcases | West | $2,459.38 | $-3,894.94 | 70.00% | 100.00% |
| Bookcases | Central | $18,776.16 | $-2,947.01 | 31.46% | 97.30% |
| Chairs | East | $28,869.88 | $-2,642.77 | 30.00% | 91.53% |

**C4. Có pattern lỗ nào xảy ra dù không discount cao không?**  
**Hàm ý:** những dòng lỗ dưới 30% discount gợi ý vấn đề khác ngoài discount, nhưng cần thêm cost/freight để kết luận nguyên nhân.

| sub_category | region | state | total_sales | total_profit | average_discount | loss_line_rate |
| --- | --- | --- | --- | --- | --- | --- |
| Tables | West | California | $16,759.50 | $-1,651.02 | 20.00% | 100.00% |
| Chairs | West | California | $12,346.45 | $-1,462.45 | 20.00% | 100.00% |
| Chairs | South | Florida | $3,641.06 | $-478.34 | 20.00% | 100.00% |
| Bookcases | East | New York | $11,247.98 | $-466.22 | 20.00% | 100.00% |
| Bookcases | West | California | $5,881.15 | $-328.70 | 15.00% | 100.00% |
| Chairs | West | Arizona | $2,334.87 | $-327.34 | 20.00% | 100.00% |
| Chairs | West | Washington | $3,602.62 | $-294.22 | 20.00% | 100.00% |
| Furnishings | East | Pennsylvania | $2,723.11 | $-274.18 | 20.00% | 100.00% |
| Chairs | South | Tennessee | $1,735.80 | $-212.53 | 20.00% | 100.00% |
| Bookcases | South | Florida | $1,484.08 | $-141.23 | 20.00% | 100.00% |

## D. Địa lý

**D1-D2. Region/state nào có lợi nhuận sau khi xét margin, và state nào doanh thu đáng kể nhưng âm profit?**  
**Hàm ý:** Central và các state điểm cao cần worklist quản trị riêng thay vì scale doanh thu tự động.

| region | total_sales | total_profit | profit_margin | average_discount | loss_line_rate |
| --- | --- | --- | --- | --- | --- |
| West | $252,612.74 | $11,504.95 | 4.55% | 13.14% | 21.92% |
| East | $208,291.20 | $3,046.17 | 1.46% | 15.41% | 30.62% |
| Central | $163,797.16 | $-2,871.05 | -1.75% | 29.74% | 65.90% |
| South | $117,298.68 | $6,771.21 | 5.77% | 12.15% | 17.47% |

| state | region | total_sales | total_profit | profit_margin | average_discount | loss_line_rate | priority_score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Texas | Central | $60,593.29 | $-10,436.14 | -17.22% | 42.30% | 97.03% | 5 |
| Illinois | Central | $28,274.52 | $-9,076.29 | -32.10% | 46.83% | 98.37% | 5 |
| Pennsylvania | East | $39,354.93 | $-7,196.72 | -18.29% | 27.68% | 52.00% | 5 |
| Ohio | East | $24,199.15 | $-4,206.32 | -17.38% | 28.49% | 56.99% | 5 |
| North Carolina | South | $15,155.48 | $-3,486.46 | -23.00% | 23.81% | 33.33% | 5 |
| Arizona | West | $13,525.29 | $-2,744.92 | -20.29% | 28.57% | 42.86% | 5 |
| Colorado | West | $13,243.04 | $-2,683.13 | -20.26% | 31.18% | 35.29% | 4 |
| Florida | South | $22,987.04 | $-2,254.98 | -9.81% | 23.24% | 32.94% | 4 |
| Tennessee | South | $13,506.73 | $-2,208.63 | -16.35% | 23.56% | 35.56% | 4 |
| Oregon | West | $6,338.13 | $-1,487.58 | -23.47% | 34.29% | 61.90% | 4 |

**D3-D4. State lỗ nặng có discount cao, sub-category cụ thể, hay cả hai? Tổ hợp region-product nào nên mở rộng/bảo vệ/review/giảm?**  
**Hàm ý:** dùng heatmap region x sub-category và state x sub-category để phân nhóm hành động: mở rộng ô xanh, bảo vệ ô profit cao, review/giảm ô âm sâu.

| state | sub_category | total_sales | total_profit | profit_margin | average_discount | loss_line_rate |
| --- | --- | --- | --- | --- | --- | --- |
| New York | Tables | $13,779.02 | $-4,535.64 | -32.92% | 40.00% | 100.00% |
| Illinois | Tables | $6,550.67 | $-4,309.74 | -65.79% | 50.00% | 100.00% |
| North Carolina | Tables | $9,681.73 | $-3,684.25 | -38.05% | 40.00% | 100.00% |
| Texas | Furnishings | $3,766.72 | $-3,312.68 | -87.95% | 60.00% | 100.00% |
| Pennsylvania | Bookcases | $5,230.76 | $-2,896.76 | -55.38% | 50.00% | 100.00% |
| Ohio | Tables | $7,887.11 | $-2,715.33 | -34.43% | 40.00% | 100.00% |
| Tennessee | Tables | $6,214.36 | $-2,663.41 | -42.86% | 40.00% | 100.00% |
| Illinois | Furnishings | $2,877.98 | $-2,631.98 | -91.45% | 60.00% | 100.00% |
| Pennsylvania | Tables | $8,052.19 | $-2,588.75 | -32.15% | 40.00% | 100.00% |
| Texas | Chairs | $26,572.45 | $-2,515.65 | -9.47% | 30.00% | 93.44% |

## E. Khách hàng và segment

**E1. Consumer, Corporate, Home Office khác nhau thế nào?**  
**Hàm ý:** segment có margin/loss-rate tốt hơn nên là nền cho cross-sell có mục tiêu.

| segment | total_sales | total_profit | profit_margin | average_discount | loss_line_rate |
| --- | --- | --- | --- | --- | --- |
| Consumer | $391,049.31 | $6,991.08 | 1.79% | 17.67% | 34.77% |
| Corporate | $229,019.79 | $7,584.82 | 3.31% | 17.41% | 32.66% |
| Home Office | $121,930.70 | $3,875.38 | 3.18% | 16.50% | 32.04% |

**E2. Repeat customers đóng góp bao nhiêu hoạt động?**  
Repeat customers chiếm 89.17% tổng số đơn trong cửa sổ dữ liệu.  
**Hàm ý:** có cơ sở để ưu tiên retention/cross-sell thay vì blanket discount.

| is_repeat_customer | customers | orders | total_sales | total_profit | profit_margin | order_share |
| --- | --- | --- | --- | --- | --- | --- |
| False | 191 | 191 | $90,892.27 | $-2,108.04 | -2.32% | 10.83% |
| True | 516 | 1,573 | $651,107.53 | $20,559.31 | 3.16% | 89.17% |

**E3-E4. Khách hàng nào sales cao nhưng profit thấp/âm, và nhóm nào phù hợp cross-sell?**  
**Hàm ý:** dùng nhãn ẩn danh để review thương mại mà không phơi bày tên khách hàng không cần thiết.

| customer_label | segment | customer_orders | customer_sales | customer_profit | customer_margin |
| --- | --- | --- | --- | --- | --- |
| KH-014 | Consumer | 1 | $4,297.64 | $-1,862.31 | -43.33% |
| KH-026 | Consumer | 3 | $3,631.59 | $-1,768.45 | -48.70% |
| KH-030 | Corporate | 2 | $3,336.32 | $-1,125.80 | -33.74% |
| KH-043 | Home Office | 4 | $2,888.11 | $-1,094.90 | -37.91% |
| KH-075 | Corporate | 4 | $2,313.50 | $-1,034.12 | -44.70% |
| KH-180 | Home Office | 2 | $1,418.54 | $-793.65 | -55.95% |
| KH-110 | Consumer | 4 | $1,935.31 | $-730.95 | -37.77% |
| KH-141 | Corporate | 3 | $1,735.56 | $-689.65 | -39.74% |
| KH-153 | Consumer | 3 | $1,618.27 | $-661.80 | -40.90% |
| KH-007 | Consumer | 4 | $4,899.12 | $-621.94 | -12.70% |

| customer_label | segment | customer_orders | customer_sales | customer_profit | customer_margin |
| --- | --- | --- | --- | --- | --- |
| KH-006 | Corporate | 7 | $5,387.39 | $1,146.49 | 21.28% |
| KH-002 | Consumer | 5 | $6,920.14 | $968.08 | 13.99% |
| KH-010 | Consumer | 5 | $4,513.11 | $805.98 | 17.86% |
| KH-009 | Corporate | 5 | $4,768.50 | $770.15 | 16.15% |
| KH-016 | Home Office | 5 | $4,132.06 | $750.26 | 18.16% |
| KH-028 | Consumer | 4 | $3,557.14 | $738.84 | 20.77% |
| KH-017 | Corporate | 6 | $4,078.82 | $720.58 | 17.67% |
| KH-001 | Consumer | 9 | $8,332.09 | $688.40 | 8.26% |
| KH-046 | Consumer | 3 | $2,852.39 | $688.14 | 24.13% |
| KH-065 | Corporate | 4 | $2,530.59 | $677.56 | 26.77% |

## F. Fulfillment context

**F1-F2. Shipping mode hoặc shipping days có khác biệt đáng kể về sales, profit, loss rate không?**  
Các bảng dưới đây là mô tả quan sát, không phải kết luận chi phí vận chuyển vì dữ liệu không có freight-cost field.  
**Hàm ý:** nếu mode hoặc số ngày giao hàng có loss-rate cao, nên xem như tín hiệu drill-down chứ không quy kết nguyên nhân.

| ship_mode | total_sales | total_profit | profit_margin | shipping_days_avg | loss_line_rate |
| --- | --- | --- | --- | --- | --- |
| Standard Class | $435,831.47 | $10,360.72 | 2.38% | 4 | 33.65% |
| Second Class | $156,289.02 | $4,226.26 | 2.70% | 3 | 32.79% |
| First Class | $110,730.52 | $3,066.95 | 2.77% | 2 | 33.94% |
| Same Day | $39,148.78 | $797.35 | 2.04% | 0 | 36.13% |

| shipping_days | total_sales | total_profit | profit_margin | loss_line_rate |
| --- | --- | --- | --- | --- |
| 0 | $37,004.68 | $539.38 | 1.46% | 36.21% |
| 1 | $25,113.83 | $784.14 | 3.12% | 32.47% |
| 2 | $124,888.12 | $7,483.90 | 5.99% | 32.90% |
| 3 | $58,159.14 | $-299.05 | -0.51% | 32.80% |
| 4 | $212,148.65 | $4,890.38 | 2.31% | 36.61% |
| 5 | $161,316.71 | $137.95 | 0.09% | 34.12% |
| 6 | $80,647.73 | $4,108.47 | 5.09% | 29.66% |
| 7 | $42,720.92 | $806.11 | 1.89% | 27.13% |
