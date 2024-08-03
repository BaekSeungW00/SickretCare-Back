#!/bin/bash

# Django 프로젝트 디렉토리로 이동
cd SickretCare-Back/

# 가상 환경 활성화 (필요한 경우)
source venv/bin/activate

# Django 데이터베이스 마이그레이션
echo "Running migrations..."
python manage.py migrate

# 서버 실행 (개발 서버)
echo "Starting the Django development server..."
python manage.py runserver 0.0.0.0:8000