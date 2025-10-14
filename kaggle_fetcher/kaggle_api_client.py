"""Utility functions to interact with the Kaggle API for downloading data,
fetching notebooks, datasets, and accessing leaderboards.
"""

import time
from urllib.error import HTTPError
from kaggle.api.kaggle_api_extended import KaggleApi


def interact_with_kaggle_api(func):
    """
    Decorator to initialize and authenticate the Kaggle API before executing
    the wrapped function. Includes basic error handling.
    """
    def wrapper(*args, **kwargs):
        print("Making Kaggle API call...")
        api = KaggleApi()
        try:
            api.authenticate()
        except Exception as e:
            print(f"Failed to authenticate Kaggle API: {e}")
            return None

        try:
            result = func(api, *args, **kwargs)
            print("Data fetched successfully.")
            return result
        except Exception as e:
            print(f"Error during Kaggle API call in {func.__name__}: {e}")
            return None

    return wrapper


def with_retries(max_retries=3, backoff_factor=1.5):
    """
    Decorator to retry a function with exponential backoff if it fails.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except HTTPError as e:
                    print(f"HTTPError: {e}. Retrying ({attempt + 1}/{max_retries})...")
                except Exception as e:
                    print(f"Error in {func.__name__}: {e}. Retrying ({attempt + 1}/{max_retries})...")

                # Only sleep if we're retrying, not after success
                sleep_time = backoff_factor * (2 ** attempt)
                time.sleep(sleep_time)

            print(f"Failed after {max_retries} attempts in {func.__name__}.")
            return None
        return wrapper
    return decorator


@interact_with_kaggle_api
@with_retries(max_retries=3, backoff_factor=1.5)
def get_notebooks_info(api, competition_slug: str, page: int = 1, page_size: int = 20):
    """
    Fetches public notebooks for the given competition with retry logic.

    Args:
        api: KaggleApi instance (injected by decorator).
        competition_slug (str): The competition slug.
        page (int): Page number.
        page_size (int): Number of notebooks per page.

    Returns:
        List of dictionaries containing notebook metadata, or None if failed.
    """
    return api.kernels_list(competition=competition_slug, page=page, page_size=page_size)


@interact_with_kaggle_api
def get_leaderboard_info(api, competition_slug: str):
    """
    Fetches the top leaderboard entries for the given competition (max 50 entries).

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): The Kaggle competition identifier.

    Returns:
        List of leaderboard entries (dicts), or [] if failed.
    """
    try:
        return api.competition_leaderboard(competition=competition_slug, max_results=50)
    except Exception as e:
        print(f"Error fetching leaderboard: {e}")
        return []


@interact_with_kaggle_api
def get_user_submissions(api, competition_slug: str):
    """
    Fetches the authenticated user's submissions for a given competition.

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): The Kaggle competition identifier.

    Returns:
        List of submission objects with:
            - publicScore: Public leaderboard score
            - privateScore: Private leaderboard score (if available)
            - date: Submission timestamp
            - description: Submission description
            - fileName: Submitted file name
    """
    try:
        submissions = api.competition_submissions(competition=competition_slug)
        
        # Convert to dict format for easier use
        submission_data = []
        for sub in submissions:
            submission_data.append({
                'date': getattr(sub, 'date', None),
                'description': getattr(sub, 'description', ''),
                'fileName': getattr(sub, 'fileName', ''),
                'publicScore': getattr(sub, 'publicScore', None),
                'privateScore': getattr(sub, 'privateScore', None),
                'status': getattr(sub, 'status', 'unknown')
            })
        
        return submission_data
    except Exception as e:
        print(f"Error fetching user submissions: {e}")
        return []


@interact_with_kaggle_api
def get_user_progress_summary(api, competition_slug: str):
    """
    Gets a comprehensive progress summary for the user in a competition.
    
    Combines:
    - User's submission history with scores
    - User's current leaderboard rank (if available)
    - Progress indicators (improving/stagnating)
    
    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): The Kaggle competition identifier.
    
    Returns:
        Dict with:
            - submissions: List of user submissions
            - best_score: Best public score achieved
            - latest_score: Most recent public score
            - submission_count: Total submissions
            - is_improving: Boolean indicating improvement trend
            - stagnation_count: Number of submissions without improvement
    """
    try:
        submissions = api.competition_submissions(competition=competition_slug)
        
        if not submissions:
            return {
                'submissions': [],
                'best_score': None,
                'latest_score': None,
                'submission_count': 0,
                'is_improving': False,
                'stagnation_count': 0,
                'error': 'No submissions found'
            }
        
        # Extract scores
        submission_data = []
        scores = []
        
        for sub in submissions:
            pub_score = getattr(sub, 'publicScore', None)
            submission_data.append({
                'date': getattr(sub, 'date', None),
                'description': getattr(sub, 'description', ''),
                'publicScore': pub_score,
                'status': getattr(sub, 'status', 'unknown')
            })
            if pub_score is not None:
                scores.append(float(pub_score))
        
        # Analyze progress
        if scores:
            # Sort by submission order (assuming submissions are in reverse chronological order)
            scores_chronological = list(reversed(scores))
            
            best_score = max(scores)
            latest_score = scores[0]  # Most recent
            
            # Detect stagnation: count submissions since last improvement
            stagnation_count = 0
            for i in range(len(scores) - 1):
                if scores[i] <= best_score:
                    stagnation_count += 1
                else:
                    break
            
            # Is improving: latest score is better than median
            median_score = sorted(scores)[len(scores) // 2] if len(scores) > 1 else scores[0]
            is_improving = latest_score > median_score if len(scores) > 1 else True
            
            return {
                'submissions': submission_data,
                'best_score': best_score,
                'latest_score': latest_score,
                'submission_count': len(submissions),
                'is_improving': is_improving,
                'stagnation_count': stagnation_count,
                'score_trend': 'improving' if is_improving else 'stagnating'
            }
        else:
            return {
                'submissions': submission_data,
                'best_score': None,
                'latest_score': None,
                'submission_count': len(submissions),
                'is_improving': False,
                'stagnation_count': len(submissions),
                'error': 'No valid scores found'
            }
            
    except Exception as e:
        print(f"Error fetching user progress: {e}")
        return {
            'submissions': [],
            'error': str(e)
        }


@interact_with_kaggle_api
def get_dataset_metadata(api, dataset_slug: str):
    """
    Fetches metadata for a specific dataset.

    Args:
        api: KaggleApi instance (injected by the decorator).
        dataset_slug (str): The Kaggle dataset identifier.

    Returns:
        Dictionary containing dataset metadata, or {} if failed.
    """
    try:
        return api.dataset_view(dataset_slug)
    except Exception as e:
        print(f"Error fetching dataset metadata: {e}")
        return {}


@interact_with_kaggle_api
def get_total_notebooks_count(api, competition_slug: str) -> int:
    """
    Gets the total number of public notebooks for a competition.

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): Identifier of the competition.

    Returns:
        int: Total number of notebooks (0 if error).
    """
    try:
        # Clean the competition slug
        clean_slug = competition_slug.replace('https://www.kaggle.com/competitions/', '')
        
        # Get kernels for this competition
        results = api.kernels_list(competition=clean_slug, page=1, page_size=1)
        
        if results:
            # Try to get total count from the response object
            if hasattr(results, 'totalCount') and isinstance(results.totalCount, int):
                return results.totalCount
            # If no totalCount, try to estimate from available kernels
            elif hasattr(results, '__len__'):
                # For a more accurate count, we could fetch more pages, but this is a start
                return len(results)
            else:
                return 1  # At least one notebook exists
        return 0
    except Exception as e:
        print(f"Error fetching total notebook count for {competition_slug}: {e}")
        return 0


@interact_with_kaggle_api
@with_retries(max_retries=2, backoff_factor=1.0)
def get_competition_data_files(api, competition_slug: str):
    """
    Fetches the list of data files for a given competition.

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): The competition slug.

    Returns:
        List of dictionaries containing file metadata, or [] if failed.
    """
    try:
        # Clean the competition slug
        clean_slug = competition_slug.replace('https://www.kaggle.com/competitions/', '')
        
        print(f"Fetching data files for competition: {clean_slug}")
        
        # Get list of data files with timeout handling
        response = api.competition_list_files(clean_slug)
        
        # The API returns an ApiListDataFilesResponse object with a 'files' attribute
        files_list = []
        if hasattr(response, 'files'):
            files_list = response.files
        elif isinstance(response, list):
            files_list = response
        else:
            # Try to iterate directly if it's iterable
            try:
                files_list = list(response)
            except (TypeError, AttributeError):
                print(f"Unexpected response type: {type(response)}")
                return []
        
        if files_list:
            # Convert to dictionaries for JSON serialization
            result = [
                {
                    'name': getattr(f, 'name', ''),
                    'size': getattr(f, 'totalBytes', 0),
                    'description': getattr(f, 'description', ''),
                    'creationDate': str(getattr(f, 'creationDate', ''))
                }
                for f in files_list
            ]
            print(f"Successfully fetched {len(result)} data files")
            return result
        else:
            print("No data files found")
            return []
    except Exception as e:
        print(f"Error fetching competition data files for {competition_slug}: {e}")
        return []


@interact_with_kaggle_api
def search_kaggle_competitions(api, query: str = "", category: str = "all", sort_by: str = "latestDeadline", page: int = 1, page_size: int = 20):
    """
    Search for Kaggle competitions.

    Args:
        api: KaggleApi instance (injected by the decorator).
        query (str): Search query for competition name/description.
        category (str): Competition category filter.
        sort_by (str): Sort by field (latestDeadline, prize, etc.).
        page (int): Page number.
        page_size (int): Number of competitions per page.

    Returns:
        List of competition dictionaries, or [] if failed.
    """
    try:
        competitions = api.competitions_list(
            category=category,
            sort_by=sort_by
        )
        
        # Filter by query if provided
        if query and competitions:
            query_lower = query.lower()
            competitions = [
                comp for comp in competitions 
                if (hasattr(comp, 'title') and query_lower in comp.title.lower()) or
                   (hasattr(comp, 'description') and query_lower in comp.description.lower()) or
                   (hasattr(comp, 'url') and query_lower in comp.url.lower())
            ]
        
        # Convert to dictionaries for JSON serialization
        if competitions:
            return [
                {
                    'slug': getattr(comp, 'ref', '').replace('https://www.kaggle.com/competitions/', '') if hasattr(comp, 'ref') else '',
                    'name': getattr(comp, 'title', ''),
                    'description': getattr(comp, 'description', ''),
                    'category': getattr(comp, 'category', ''),
                    'deadline': getattr(comp, 'deadline', ''),
                    'prize': getattr(comp, 'prize', ''),
                    'url': f"https://www.kaggle.com/competitions/{getattr(comp, 'ref', '')}",
                    'enabledDate': getattr(comp, 'enabled_date', ''),
                    'teamCount': getattr(comp, 'team_count', 0),
                    'userHasEntered': getattr(comp, 'user_has_entered', False)
                }
                for comp in competitions
            ]
        
        return []
    except Exception as e:
        print(f"Error searching competitions: {e}")
        return []


@interact_with_kaggle_api
def get_competition_details(api, competition_slug: str):
    """
    Get detailed information about a specific competition.

    Args:
        api: KaggleApi instance (injected by the decorator).
        competition_slug (str): The competition slug.

    Returns:
        Dictionary with competition details, or {} if failed.
    """
    try:
        # Find the competition in the competitions list
        competitions = api.competitions_list()
        competition = None
        
        # Clean the competition slug for comparison
        clean_slug = competition_slug.replace('https://www.kaggle.com/competitions/', '')
        
        for comp in competitions:
            # Check both full ref and cleaned ref
            comp_ref = getattr(comp, 'ref', '')
            comp_clean_ref = comp_ref.replace('https://www.kaggle.com/competitions/', '')
            
            if (comp_ref == competition_slug or 
                comp_clean_ref == competition_slug or 
                comp_clean_ref == clean_slug or
                comp_ref.endswith(competition_slug)):
                competition = comp
                break
        
        if competition:
            # Get additional info using other API methods
            notebook_count = 0
            try:
                kernels = api.kernels_list(competition=clean_slug, page=1, page_size=1)
                if kernels:
                    # Try to get total count from the response
                    if hasattr(kernels, 'totalCount'):
                        notebook_count = kernels.totalCount
                    else:
                        # If no totalCount, estimate from available kernels
                        notebook_count = len(kernels)
            except Exception as e:
                print(f"Could not get notebook count: {e}")
            
            return {
                'slug': clean_slug,
                'name': getattr(competition, 'title', ''),
                'description': getattr(competition, 'description', ''),
                'category': getattr(competition, 'category', ''),
                'deadline': getattr(competition, 'deadline', ''),
                'prize': getattr(competition, 'prize', ''),
                'url': f"https://www.kaggle.com/competitions/{clean_slug}",
                'enabledDate': getattr(competition, 'enabled_date', ''),
                'teamCount': getattr(competition, 'team_count', 0),
                'userHasEntered': getattr(competition, 'user_has_entered', False),
                'evaluationMetric': getattr(competition, 'evaluation_metric', ''),
                'maxTeamSize': getattr(competition, 'max_team_size', 1),
                'maxDailySubmissions': getattr(competition, 'max_daily_submissions', 0),
                'notebookCount': notebook_count
            }
        return {}
    except Exception as e:
        print(f"Error fetching competition details: {e}")
        return {}


