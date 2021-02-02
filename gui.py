from tkinter import *, Label, Label
from PIL import ImageTk, Image
window=Tk()


window.title('Nhận diện biển số')
window.geometry("1280x968")
# adding image (remember image should be PNG and not JPG) 
image = Image.open("images/Untitled.png")
image = image.resize((520, 280), Image.ANTIALIAS)
my_img = ImageTk.PhotoImage(image)
  
# setting image with the help of label 
Label(window, image = my_img).grid(row = 0, column = 0, 
       columnspan = 2, rowspan = 1)
Label(window, image = my_img).grid(row = 0, column = 2, 
       columnspan = 2, rowspan = 1, padx = 20, pady = 5)
# this will create a label widget 
l0 = Label(window, text = "(Ảnh minh họa)")
l01 = Label(window, text = "(Ảnh minh họa)")
l1 = Label(window, text = "BKS xe ô tô:" + "30E9221", borderwidth=1, relief="solid")
l2 = Label(window, text = "Tên chủ xe, địa chỉ: Vũ Quốc Vương, 54 Triều Khúc, Thanh Xuân, Hà Nội", borderwidth=1, relief="solid")
l3 = Label(window, text = "Tốc độ xe qua cân [km/h]:" + "160", borderwidth=1, relief="solid")
l4 = Label(window, text = "BKS SMRM/RM:")
l5 = Label(window, text = "Thời gian vào:")
l6 = Label(window, text = "THÔNG TIN KHỐI LƯỢNG VÀ KÍCH THƯỚC CHO PHÉP CỦA XE", font ="none 14 bold")
l7 = Label(window, text = "Khối lượng bản thân của ô tô [tấn]:")
l8 = Label(window, text = "Khối lượng bản thân của SMRM/RM [tấn]:")
l9 = Label(window, text = "Khối lượng số người cho phép ngồi trên ô tô [0,065 tấn x số người]")
l10 = Label(window, text = "Khối lượng HHCC cho phép TGGT của ô tô/SMRM/RM [tấn]")
l11 = Label(window, text = "Loại xe", borderwidth=1, relief="solid")
l12 = Label(window, text = "Kích thước bao (DxRxC) [m]")
l13 = Label(window, text = "Kích thước thùng hàng (DxRxC) [m]")
l14 = Label(window, text = "Chiều dài CS [m]")
l15 = Label(window, text = "Ô tô")
l16  = Label(window, text = "SMRM")
l17 = Label(window, text = "I. KẾT QUẢ CẦN KIỂM TRA XE THEO TẢI TRỌNG (TT) CHO PHÉP CỦA CẦU, ĐƯỜNG", font ="none 12 bold")
l18  = Label(window, text = "Loại trục xe")
l19  = Label(window, text = "TT cân được [tấn]")
l20  = Label(window, text = "Sai số [tấn]")
l21  = Label(window, text = "Sau trừ sai số [tấn]")
l22  = Label(window, text = "TT cho phép [tấn]")
l23  = Label(window, text = "Khối lượng quá tải [tấn]")
l24  = Label(window, text = "Phần trăm quá tải [tấn]")
l25  = Label(window, text = "Đơn 1")
l26  = Label(window, text = "Đơn 2")
l27  = Label(window, text = "Khối lượng toàn xe", font = "none 12 bold")
l28  = Label(window, text = "II. KẾT QUẢ CẦN KIỂM TRA XE THEO KHỐI LƯỢNG (KL) HÀNG CCCP TGGT")
l29  = Label(window, text = "Khối lượng hàng CC cân được [tấn]")
l30  = Label(window, text = "Vượt KL, hàng CCCP TGGT [tấn]")
l31  = Label(window, text = "Phần trăm HH CC vượt [%]")
l32  = Label(window, text = "III. KẾT LUẬN")
l33  = Label(window, text = "Người lập phiếu cân")
l34  = Label(window, text = "(Ký và ghi rõ họ tên", font = "none 12 italic")





# grid method to arrange labels in respective 
# rows and columns as specified 
# l0.gird(row = 5, column = 0, sticky = W, pady = 2)
l0.grid(row = 2, column = 0, padx = 5, pady = 2)
l01.grid(row = 2, column = 2, padx = 5, pady = 2)
l1.grid(row = 3, column = 0, sticky = W, padx = 5,pady = 2)
l2.grid(row = 4, column = 0, sticky = W, padx = 5, pady = 2)
l3.grid(row = 5, column = 0, sticky = W, padx = 5, pady = 2)
l4.grid(row = 3, column = 2, sticky = W, padx = 20, pady = 2)
l5.grid(row = 5, column = 2, sticky = W, padx = 20, pady = 2)
l6.grid(row = 6, column = 0, columnspan = 4)
l7.grid(row = 7, column = 0, sticky = W, padx = 5, pady = 2)
l8.grid(row = 7, column = 2, columnspan = 2, sticky = W, padx = 20, pady = 2)
l9.grid(row = 9, column = 0, sticky = W, padx = 5, pady = 2)
l10.grid(row = 10, column = 0, sticky = W, padx = 5, pady = 2)  
l11.grid(row = 11, rowspan = 2, column = 0, columnspan = 1, sticky = W, padx = 5, pady = 2)
l12.grid(row = 11, rowspan = 2, column = 1, sticky = W, pady = 2)
l13.grid(row = 11, rowspan = 2, column = 2, sticky = W, padx = 20, pady = 2)
l14.grid(row = 11, rowspan = 2, column = 3, sticky = W, padx = 5, pady = 2)
l15.grid(row = 13, rowspan = 1, column = 0, sticky = W, padx = 5, pady = 2)
l15.grid(row = 13, rowspan = 1, column = 0, sticky = W, padx = 5, pady = 2)
l16.grid(row = 14, rowspan = 1, column = 0, sticky = W, padx = 5, pady = 2)
l17.grid(row = 15, rowspan = 1, column = 0)

window.mainloop()