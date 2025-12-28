import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from styles import StyleManager
from widgets import Card, MetricCard, PieChart, BarChart, LineChart
import calendar

class StatisticsForm(ttk.Frame):
    """Форма статистики"""
    
    def __init__(self, parent, db, user):
        super().__init__(parent)
        self.db = db
        self.user = user
        
        self.setup_ui()
        self.refresh()
    
    def setup_ui(self):
        """Настройка интерфейса"""
        # Контейнер с прокруткой
        canvas = tk.Canvas(self, bg=StyleManager.COLORS['light'])
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, 
                                 command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Панель фильтров
        filter_card = Card(scrollable_frame, title="Фильтры")
        filter_card.pack(fill=tk.X, padx=10, pady=10)
        
        filter_frame = ttk.Frame(filter_card.content_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Период
        ttk.Label(filter_frame, text="Период:", 
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.period_var = tk.StringVar(value="month")
        period_combo = ttk.Combobox(filter_frame, textvariable=self.period_var,
                                   values=['day', 'week', 'month', 'quarter', 'year', 'all'],
                                   state='readonly',
                                   width=10)
        period_combo.pack(side=tk.LEFT, padx=(0, 20))
        period_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh())
        
        # Дата начала
        ttk.Label(filter_frame, text="С:", 
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.start_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        start_date_entry = ttk.Entry(filter_frame, textvariable=self.start_date_var,
                                    style='Modern.TEntry', width=12)
        start_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Дата окончания
        ttk.Label(filter_frame, text="По:", 
                 style='Body.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.end_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        end_date_entry = ttk.Entry(filter_frame, textvariable=self.end_date_var,
                                  style='Modern.TEntry', width=12)
        end_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Кнопка применения
        ttk.Button(filter_frame, text="Применить",
                  style='Primary.TButton',
                  command=self.refresh).pack(side=tk.LEFT)
        
        # Кнопка экспорта
        ttk.Button(filter_frame, text="📊 Экспорт",
                  style='Info.TButton',
                  command=self.export_statistics).pack(side=tk.LEFT, padx=(20, 0))
        
        # Основные метрики
        metrics_frame = ttk.Frame(scrollable_frame)
        metrics_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.total_requests_metric = MetricCard(metrics_frame, "Заявок всего", "0")
        self.total_requests_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.completed_metric = MetricCard(metrics_frame, "Завершено", "0", "%")
        self.completed_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.avg_time_metric = MetricCard(metrics_frame, "Ср. время", "0", "дн")
        self.avg_time_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.revenue_metric = MetricCard(metrics_frame, "Доход", "0", "₽")
        self.revenue_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        self.avg_revenue_metric = MetricCard(metrics_frame, "Ср. чек", "0", "₽")
        self.avg_revenue_metric.pack(side=tk.LEFT, padx=5, fill=tk.BOTH, expand=True)
        
        # Графики
        charts_frame = ttk.Frame(scrollable_frame)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Статусы заявок
        status_card = Card(charts_frame, title="Статусы заявок")
        status_card.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        self.status_chart = PieChart(status_card.content_frame, 
                                    width=300, height=300)
        self.status_chart.pack(padx=10, pady=10)
        
        # Динамика заявок
        trend_card = Card(charts_frame, title="Динамика заявок")
        trend_card.grid(row=0, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        self.trend_chart = LineChart(trend_card.content_frame,
                                    width=400, height=300)
        self.trend_chart.pack(padx=10, pady=10)
        
        # Типы техники
        tech_card = Card(charts_frame, title="Типы техники")
        tech_card.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
        
        self.tech_chart = BarChart(tech_card.content_frame,
                                  width=300, height=300)
        self.tech_chart.pack(padx=10, pady=10)
        
        # Мастера
        masters_card = Card(charts_frame, title="Эффективность мастеров")
        masters_card.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
        
        self.masters_chart = BarChart(masters_card.content_frame,
                                     width=400, height=300)
        self.masters_chart.pack(padx=10, pady=10)
        
        # Настройка сетки
        charts_frame.columnconfigure(0, weight=1)
        charts_frame.columnconfigure(1, weight=1)
        charts_frame.rowconfigure(0, weight=1)
        charts_frame.rowconfigure(1, weight=1)
    
    def refresh(self):
        """Обновить статистику"""
        try:
            stats = self._calculate_statistics()
            self._update_metrics(stats)
            self._update_charts(stats)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить статистику: {e}")
    
    def _calculate_statistics(self):
        """Расчет статистики"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Определение периода
            period = self.period_var.get()
            start_date = self.start_date_var.get()
            end_date = self.end_date_var.get()
            
            # Базовый запрос с фильтром по дате
            date_filter = ""
            params = []
            
            if start_date and end_date:
                date_filter = "WHERE r.startDate BETWEEN ? AND ?"
                params = [start_date, end_date]
            elif period != 'all':
                if period == 'day':
                    date_filter = "WHERE r.startDate = DATE('now')"
                elif period == 'week':
                    date_filter = "WHERE r.startDate >= DATE('now', '-7 days')"
                elif period == 'month':
                    date_filter = "WHERE r.startDate >= DATE('now', '-30 days')"
                elif period == 'quarter':
                    date_filter = "WHERE r.startDate >= DATE('now', '-90 days')"
                elif period == 'year':
                    date_filter = "WHERE r.startDate >= DATE('now', '-365 days')"
            
            # Общая статистика
            query = f'''
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN r.requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed_requests,
                    AVG(CASE WHEN r.completionDate IS NOT NULL 
                        THEN julianday(r.completionDate) - julianday(r.startDate) 
                        ELSE NULL END) as avg_repair_days,
                    SUM(r.actualCost) as total_revenue,
                    AVG(r.actualCost) as avg_revenue_per_request
                FROM requests r
                {date_filter}
            '''
            
            cursor.execute(query, params)
            basic_stats = dict(cursor.fetchone())
            
            # Статистика по статусам
            cursor.execute(f'''
                SELECT r.requestStatus, COUNT(*) as count
                FROM requests r
                {date_filter}
                GROUP BY r.requestStatus
                ORDER BY count DESC
            ''', params)
            
            by_status = dict(cursor.fetchall())
            
            # Статистика по типам техники
            cursor.execute(f'''
                SELECT r.homeTechType, COUNT(*) as count
                FROM requests r
                {date_filter}
                GROUP BY r.homeTechType
                ORDER BY count DESC
                LIMIT 10
            ''', params)
            
            by_tech_type = dict(cursor.fetchall())
            
            # Статистика по мастерам
            cursor.execute(f'''
                SELECT u.fio, COUNT(r.requestID) as count
                FROM users u
                LEFT JOIN requests r ON u.userID = r.masterID
                WHERE u.type = 'Мастер'
                {'AND r.startDate BETWEEN ? AND ?' if start_date and end_date else ''}
                GROUP BY u.userID
                ORDER BY count DESC
                LIMIT 10
            ''', params if start_date and end_date else [])
            
            by_masters = dict(cursor.fetchall())
            
            # Динамика по дням/неделям/месяцам
            if period in ['day', 'week', 'month']:
                group_by = "DATE(r.startDate)"
                order_by = "DATE(r.startDate)"
            else:
                group_by = "strftime('%Y-%m', r.startDate)"
                order_by = "strftime('%Y-%m', r.startDate)"
            
            cursor.execute(f'''
                SELECT {group_by} as period, COUNT(*) as count
                FROM requests r
                {date_filter}
                GROUP BY {group_by}
                ORDER BY {order_by}
            ''', params)
            
            trends = cursor.fetchall()
            
            return {
                'basic': basic_stats,
                'by_status': by_status,
                'by_tech_type': by_tech_type,
                'by_masters': by_masters,
                'trends': trends
            }
    
    def _update_metrics(self, stats):
        """Обновление метрик"""
        basic = stats['basic']
        
        total = basic['total_requests'] or 0
        completed = basic['completed_requests'] or 0
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        self.total_requests_metric.update_value(total)
        self.completed_metric.update_value(f"{completion_rate:.1f}")
        self.avg_time_metric.update_value(f"{basic['avg_repair_days'] or 0:.1f}")
        self.revenue_metric.update_value(f"{basic['total_revenue'] or 0:,.0f}")
        self.avg_revenue_metric.update_value(f"{basic['avg_revenue_per_request'] or 0:,.0f}")
    
    def _update_charts(self, stats):
        """Обновление графиков"""
        # Статусы заявок
        self.status_chart.set_data(stats['by_status'])
        
        # Типы техники
        self.tech_chart.set_data(stats['by_tech_type'])
        
        # Мастера
        self.masters_chart.set_data(stats['by_masters'])
        
        # Динамика
        if stats['trends']:
            trend_data = [(str(row[0]), row[1]) for row in stats['trends']]
            self.trend_chart.set_data(trend_data, StyleManager.COLORS['secondary'])
    
    def generate_daily_report(self):
        """Создание ежедневного отчета"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                    SUM(actualCost) as revenue
                FROM requests 
                WHERE DATE(startDate) = ?
            ''', (today,))
            
            stats = cursor.fetchone()
            
            report = f"""
            📊 Ежедневный отчет
            Дата: {today}
            
            Статистика за день:
            • Всего заявок: {stats[0] or 0}
            • Завершено: {stats[1] or 0}
            • Доход: {stats[2] or 0:.2f}₽
            
            Новые заявки сегодня:
            """
            
            cursor.execute('''
                SELECT requestID, homeTechType, problemDescription
                FROM requests 
                WHERE DATE(startDate) = ?
                ORDER BY requestID
            ''', (today,))
            
            for row in cursor.fetchall():
                report += f"\n• #{row[0]} - {row[1]}: {row[2][:50]}..."
            
            messagebox.showinfo("Ежедневный отчет", report)
    
    def generate_masters_report(self):
        """Отчет по мастерам"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    u.fio,
                    COUNT(r.requestID) as total,
                    SUM(CASE WHEN r.requestStatus = 'Готова к выдаче' THEN 1 ELSE 0 END) as completed,
                    AVG(CASE WHEN r.completionDate IS NOT NULL 
                        THEN julianday(r.completionDate) - julianday(r.startDate) 
                        ELSE NULL END) as avg_days,
                    SUM(r.actualCost) as revenue
                FROM users u
                LEFT JOIN requests r ON u.userID = r.masterID
                WHERE u.type = 'Маster'
                GROUP BY u.userID
                ORDER BY completed DESC, revenue DESC
            ''')
            
            report = "📊 Отчет по мастерам\n\n"
            report += "Мастер | Всего | Завершено | Ср. время | Доход\n"
            report += "-" * 60 + "\n"
            
            for row in cursor.fetchall():
                report += f"{row[0]} | {row[1]} | {row[2]} | {row[3]:.1f} дн | {row[4]:,.0f}₽\n"
            
            messagebox.showinfo("Отчет по мастерам", report)
    
    def generate_tech_report(self):
        """Отчет по технике"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT 
                    homeTechType,
                    COUNT(*) as count,
                    AVG(CASE WHEN completionDate IS NOT NULL 
                        THEN julianday(completionDate) - julianday(startDate) 
                        ELSE NULL END) as avg_days,
                    AVG(actualCost) as avg_cost,
                    SUM(actualCost) as total_cost
                FROM requests 
                GROUP BY homeTechType
                ORDER BY count DESC
            ''')
            
            report = "📊 Отчет по типам техники\n\n"
            report += "Техника | Количество | Ср. время | Ср. стоимость | Всего\n"
            report += "-" * 70 + "\n"
            
            for row in cursor.fetchall():
                report += f"{row[0]} | {row[1]} | {row[2]:.1f} дн | {row[3]:,.0f}₽ | {row[4]:,.0f}₽\n"
            
            messagebox.showinfo("Отчет по технике", report)
    
    def export_statistics(self):
        """Экспорт статистики"""
        from utils.exporters import DataExporter
        
        exporter = DataExporter(self.db)
        filename = exporter.export_statistics()
        
        if filename:
            messagebox.showinfo("Экспорт", 
                              f"Статистика экспортирована:\n{filename}")