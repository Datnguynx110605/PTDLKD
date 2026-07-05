
# Báo cáo chất lượng dữ liệu

## Nguồn dữ liệu

- Tệp nguồn: `Dataset.csv`
- SHA-256: `64764de9612919ec940f08191bb728bcb5579e682a630706ee624f8f13d7dc4f`
- Encoding: `cp1252`
- Định dạng ngày: `%m/%d/%Y`
- Thời điểm xử lý UTC: `2026-07-05T14:39:34+00:00`

## Kiểm tra raw file

| Chỉ số | Giá trị |
|---|---:|
| Dòng | 2,121 |
| Cột | 21 |
| Giá trị thiếu | 0 |
| Dòng trùng lặp | 0 |
| Row ID trùng lặp | 0 |
| Đơn hàng duy nhất | 1,764 |
| Khách hàng duy nhất | 707 |
| Tổng doanh thu | $741,999.80 |
| Tổng lợi nhuận | $18,451.27 |
| Dòng lỗ | 714 |

## Kết luận

Dữ liệu đầu vào đạt các ràng buộc bắt buộc: Furniture-only, không có giá trị thiếu, không có `Row ID` trùng lặp, ngày giao hàng không sớm hơn ngày đặt hàng, và các tổng doanh thu/lợi nhuận khớp baseline trong `CONTEXT.md`.

Bảng fact sau biến đổi có 2,121 dòng và giữ nguyên tổng doanh thu $741,999.80 cùng tổng lợi nhuận $18,451.27.
