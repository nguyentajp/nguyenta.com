---
# Mẫu front matter cho bài viết mới. Tạo bài bằng:
#   hugo new content content/vi/posts/ten-bai/index.md
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
# translationKey nối bản tiếng Việt với bản tiếng Nhật của cùng một bài.
translationKey: "{{ .File.ContentBaseName }}"
slug: "{{ .File.ContentBaseName }}"
# description dùng cho đoạn giới thiệu, thẻ Open Graph và kết quả tìm kiếm.
description: ""
# Chọn một trong: hoc-tap, doi-song, du-lich, suy-nghi, nhat-ky
# (tiếng Nhật: manabi, kurashi, tabi, shisaku, nikki)
categories: []
# Thẻ viết tự nhiên, có dấu: ["osaka", "mùa thu"]
tags: []
# Ảnh bìa: tên một file ảnh trong thư mục bài, ví dụ "minoo.jpg".
# Để trống thì lấy ảnh đầu tiên trong bài.
cover: ""
draft: true
---
