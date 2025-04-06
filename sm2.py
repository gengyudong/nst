from supermemo2 import first_review, review
from datetime import datetime

# Example 1: Using first_review with a specific date
review_date = datetime(2025, 4, 1)
result = first_review(4, review_date)

# Print the result dictionary to see available keys
print(f"First review on: {review_date.strftime('%Y-%m-%d')}")
print(f"Result dictionary: {result}")  # See all available keys

# The review_datetime is a string, we need to convert it to a datetime object
next_review_str = result.get('review_datetime', result.get('datetime', None))
if not next_review_str:
    print("Could not find review date key. Available keys:", result.keys())
else:
    # Convert string to datetime object
    next_review = datetime.strptime(next_review_str, '%Y-%m-%d %H:%M:%S')
    
    print(f"Next review date: {next_review.strftime('%Y-%m-%d')}")
    print(f"Easiness factor: {result['easiness']}")  # Note: using 'easiness' instead of 'ef'
    print(f"Interval: {result['interval']} days")
    print(f"Repetitions: {result['repetitions']}")

    # Example 2: Manual tracking of multiple reviews
    # Store values from first review
    easiness = result['easiness']  # Note: using 'easiness' instead of 'ef'
    interval = result['interval'] 
    repetitions = result['repetitions']
    
    print("\nReview Schedule:")
    print(f"Review #1 ({review_date.strftime('%Y-%m-%d')}): " +
          f"Quality=4, Next={next_review.strftime('%Y-%m-%d')}, " +
          f"Interval={interval} days, EF={round(easiness, 2)}")
    
    # For subsequent reviews, manually pass the previous values
    next_review_date = next_review
    for i in range(2, 6):
        review_date = next_review_date
        quality = [3, 5, 4, 3][i-2]  # Qualities for reviews 2-5
        
        # Use the standalone review function
        result = review(quality, easiness, interval, repetitions, review_date)
        
        # Look for the correct date key and convert from string to datetime
        next_review_str = result.get('review_datetime', result.get('datetime', None))
        if not next_review_str:
            print(f"Review #{i}: Could not find review date key. Available keys:", result.keys())
            break
            
        next_review_date = datetime.strptime(next_review_str, '%Y-%m-%d %H:%M:%S')
        
        # Update values for next review
        easiness = result['easiness']  # Note: using 'easiness' instead of 'ef'
        interval = result['interval']
        repetitions = result['repetitions']
        
        print(f"Review #{i} ({review_date.strftime('%Y-%m-%d')}): " +
              f"Quality={quality}, Next={next_review_date.strftime('%Y-%m-%d')}, " +
              f"Interval={interval} days, EF={round(easiness, 2)}")