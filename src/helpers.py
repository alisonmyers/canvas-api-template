from canvasapi import Canvas
import util
import sys
import pandas as pd
import ast

def create_instance(API_URL, API_KEY):
    try:
        canvas = Canvas(API_URL, API_KEY)
        util.print_success("Token Valid: {}".format(str(canvas.get_user('self'))))
        return(canvas)
    except Exception as e:
        util.print_error("\nInvalid Token: {}\n{}".format(API_KEY, str(e)))
        sys.exit(1)
        #raise

def _get_course(canvas_obj, course_id):
    '''
    Get Canvas course using canvas object from canvasapi
    Parameters:
        course (Canvas): canvasapi instance
        course_id (int): Canvas course ID
    Returns:
        canvasapi.course.Course object
    '''
    try:
        course = canvas_obj.get_course(course_id)
        util.print_success(f'Entered id: {course_id}, Course: {course.name}.')
    except Exception:
        util.shut_down(f'ERROR: Could not find course [ID: {course_id}]. Please check course id.')

    return course

def all_dict_to_str(d):
    """
        Canvas JSON Helper
        Handles dictionaries returned from canvas.
        When data returned some items are not strings - changes all items to strings.
        Some data becomes string in DataFrames i.e. "{'a': 'string'}", transforms to dict.
        Returns Dict where all values are strings.
     """
    # if its a dict, change items to strings
    if isinstance(d, dict):
        new = {k:str(v) for k, v in d.items()}
        return(new)
    else:
        if pd.isnull(d):
            pass
        else:
            d = ast.literal_eval(d)
            new = {k:str(v) for k, v in d.items()}
            return(new)

# Working with DataFrames and 
def list_to_df(df, col_to_expand):
    """
    Canvas JSON Helper
    Expands column that contains list to multiple rows (1/list item)
    Keeps original columns. 
    Requires df and col_to_expand (the column that contains lists)
    Returns DataFrame with original index
    """
    s = df.apply(lambda x: pd.Series(x[col_to_expand]),axis=1).stack().reset_index(level=1, drop=True)
    s.name = col_to_expand
    new_df = df.drop(col_to_expand, axis=1).join(s)
    return(new_df)
        

def dict_to_cols(df, col_to_expand, expand_name):
    """
    Canvas JSON Helper
    Expands column that contains dict to multiple columns (1/dict key)
    Handles transforming column specified to appropriate dict (where all items are strings)
    Returns DataFrame with original index
    """
    df[col_to_expand] = df[col_to_expand].apply(all_dict_to_str, axis=1)
    original_df = df.drop([col_to_expand], axis=1)
    extended_df = df[col_to_expand].apply(pd.Series)
    extended_df.columns = [i if bool(re.search(expand_name, i)) else "{}{}".format(str(expand_name), str(i))for i in extended_df.columns]
    new_df = pd.concat([original_df, extended_df], axis=1, ignore_index=False)
    return(new_df)
