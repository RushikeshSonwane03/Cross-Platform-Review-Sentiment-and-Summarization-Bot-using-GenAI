# myapp/views.py
import pandas as pd
from django.shortcuts import render
from django.contrib import messages
from core.Sentiment.sentiment import analyze_sentiments  # Import the sentiment function
from core.Summarization.summarizer import generate_summary  # import your summarizer

data = None          # Global to hold CSV data
processed_data = None  # Global to hold sentiment result
platform = None
selected_platform = None
summary = None


def home(request):
    return render(request, 'index.html')

def load_csv(request):
    global data
    global selected_platform
    global platform
    selected_platform = request.GET.get('platform')
    platform_data = None
    platforms = []

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        try:
            df = pd.read_csv(csv_file)
            request.session['csv_data'] = df.to_json()  # Save to session
            global data
            data = df
            platforms = df['platform'].unique().tolist()
        except Exception as e:
            messages.error(request, f"Error reading CSV: {e}")
    elif request.session.get('csv_data'):
        df = pd.read_json(request.session['csv_data'])
        data = df
        platforms = df['platform'].unique().tolist()
        if selected_platform:
            platform_data = df[df['platform'] == selected_platform].tail()


    elif data is not None:
        platforms = data['platform'].unique().tolist()
        if selected_platform:
            platform_data = data[data['platform'] == selected_platform].tail()

    return render(request, 'upload.html', {
        'data': platform_data,
        'platforms': platforms,
        'selected_platform': selected_platform
    })


def process(request):
    print("IN Process")

    if 'csv_data' not in request.session:
        messages.error(request, "No CSV file loaded. Please upload a CSV first.")
        print("No CSV file loaded. Please upload a CSV first.")
        return render(request, 'index.html')

    platform = request.POST.get('platform') or request.GET.get('platform')

    if not platform:
        messages.error(request, "No platform selected.")
        return render(request, 'upload.html', {
            'data': None,
            'platforms': pd.read_json(request.session['csv_data'])['platform'].unique().tolist()
        })

    try:
        df = pd.read_json(request.session['csv_data'])
        platform_df = df[df['platform'] == platform].copy()
        global processed_data
        processed_data = analyze_sentiments(platform_df, text_col='review_text', rating_col='rating')
        # print("\n ------------------------------------------------------------------ \n")
        # print(processed_data)
        # print(type(processed_data))
        # print("\n ------------------------------------------------------------------ \n")
    except Exception as e:
        messages.error(request, f"Error during sentiment analysis: {e}")
        return render(request, 'index.html')

    return render(request, 'sentiment_output.html', {
    'processed': processed_data[['review_text_cleaned', 'sentiment', 'neg', 'neu', 'pos']].head(10).values.tolist(),
    'selected_platform': platform
    })

# Cleaning the summary text, removing all "*" (astricks) and "#" (hashtags).
def clean_summary_text(summary: str) -> str:
    cleaned = summary.replace('*', '').replace('#', '')
    return cleaned

# Assuming 'data' still holds the last uploaded dataframe
def summarize_reviews(request):

    if data is None:
        messages.error(request, "No review data found. Please upload a file first.")
        return render(request, 'index.html')

    print("[INFO] Generating summary...")
    global summary
    summary_response = generate_summary(data)
    summary = clean_summary_text(summary_response)
    # print(summary)

    return render(request, 'summarized.html', {
        'summary': summary
    })


def final_report_view(request):
    try:
        global data
        global processed_data
        global platform
        global selected_platform
        global summary

        if data is None or processed_data is None or selected_platform is None or summary is None:
            messages.error(request, "Missing data for final report. Ensure CSV is uploaded and processed.")
            return render(request, 'index.html')

        # Filter processed data for selected platform
        platform_data = processed_data[processed_data['platform'] == selected_platform]

        # Select top 10 or required fields
        sentiment_table = platform_data[['review_text_cleaned', 'sentiment', 'neg', 'neu', 'pos']].head(10).values.tolist()

        # Chart image filenames (ensure they are saved under 'static/images/' during earlier processing)
        # chart_paths = {
        #     'chart1': 'static/sentiment_graphs/images/sentiment_pie_chart.png',
        #     'chart2': 'static/sentiment_graphs/images/ratings_distribution.png',
        #     'chart3': 'static/sentiment_graphs/images/sentiment_trend_over_time.png'
        # }

        # Data to be passed to template
        report_data = {
            'selected_platform': selected_platform,
            'sentiment_table': sentiment_table,
            # 'chart1': chart_paths['chart1'],
            # 'chart2': chart_paths['chart2'],
            # 'chart3': chart_paths['chart3'],
            'summary': summary
        }

        return render(request, 'final_report.html', report_data)

    except Exception as e:
        return render(request, 'error.html', {'message': f'Final report failed: {str(e)}'})
