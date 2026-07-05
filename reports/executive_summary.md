
# Tóm tắt điều hành

## Phạm vi và câu hỏi quyết định

Phân tích này chỉ bao phủ danh mục `Furniture` trong `Dataset.csv`. Mục tiêu là tìm cách tăng doanh thu mà không hy sinh lợi nhuận, dựa trên dữ liệu quan sát được. Các kết luận về giảm giá là mối quan hệ mô tả, không phải bằng chứng nhân quả vì dữ liệu không có COGS, phí vận chuyển, marketing spend hoặc returns.

## KPI tổng quan

| KPI | Giá trị |
|---|---:|
| Doanh thu | $741,999.80 |
| Lợi nhuận | $18,451.27 |
| Biên lợi nhuận có trọng số | 2.49% |
| Đơn hàng | 1,764 |
| Khách hàng | 707 |
| AOV | $420.63 |
| Dòng lỗ | 714 |
| Tỷ lệ dòng lỗ | 33.66% |

## Phát hiện chính

- **Sự thật quan sát:** Năm 2017 đạt doanh thu $215,387.27 nhưng lợi nhuận chỉ $3,018.39 và biên lợi nhuận 1.40%.
- **Sự thật quan sát:** `Tables` lỗ $-17,725.48 và `Bookcases` lỗ $-3,472.56; đây là hai nhóm cần sửa chữa lợi nhuận.
- **Sự thật quan sát:** `Central` là vùng lỗ tổng thể với lợi nhuận $-2,871.05 và mean discount 29.74%.
- **Sự thật quan sát:** Discount 30% tạo lợi nhuận $-10,695.32; nhóm discount >=30% tạo lợi nhuận $-54,477.76 với tỷ lệ dòng lỗ 97.23%.
- **Giả thuyết có bằng chứng:** Giảm giá cao có liên quan mạnh với lợi nhuận âm, nhưng cơ chế đầy đủ cần dữ liệu chi phí và vận chuyển để xác nhận.

## Bảng ưu tiên tiểu bang

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

Xem `reports/business_questions.md` để có câu trả lời chi tiết cho toàn bộ nhóm câu hỏi A-F trong `CONTEXT.md`.
