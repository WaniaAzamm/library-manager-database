import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="Simple Library Manager",
    page_icon="📚",
    layout="wide"
)

st.markdown("""
<style>
    .stApp {
        background-color: black;
    }
    
    /* Make all text white */
    p, li, .stSelectbox, .stTextInput, .stNumberInput, .stRadio, .stCheckbox, .stSelectbox label, .stTextInput label, .stNumberInput label {
        color: white !important;
    }
    
    /* Make headings purple */
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        text-align: center;
    }
    
    h1 {
        font-size: 2.5rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        font-size: 1.4rem;
    }
    
    /* Improve card styling */
    .simple-card {
        background-color: #121212;
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #a020f0;
    }
    
    .stButton > button {
        background-color: #a020f0;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #8000d0;
        box-shadow: 0 4px 8px rgba(160, 32, 240, 0.3);
    }
    
    /* Improve table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        color: white;
    }
    
    .dataframe th {
        background-color: #a020f0;
        color: white;
        text-align: center;
        padding: 12px;
    }
    
    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid #333;
        color: white;
    }
    
    /* Improve book card styling */
    .book-card {
        background-color: #121212;
        border-radius: 10px;
        padding: 20px;
        height: 100%;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #a020f0;
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(160, 32, 240, 0.4);
    }
    
    .book-card h3 {
        margin-top: 0;
        color: #a020f0;
        font-size: 1.3rem;
        text-align: left;
    }
    
    .book-card p {
        margin-bottom: 12px;
        color: white;
        font-size: 1.05rem;
    }
    
    .book-card .status-read {
        color: #4CAF50;
        font-weight: 500;
    }
    
    .book-card .status-unread {
        color: #FF5722;
        font-weight: 500;
    }
    
    .sidebar .stButton > button {
        width: 100%;
    }
    
    /* Improve metric card styling */
    .metric-card {
        background-color: #121212;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-top: 4px solid #a020f0;
    }
    
    .metric-card h3 {
        margin-top: 0;
        color: white;
    }
    
    .metric-card p {
        font-size: 2rem;
        font-weight: bold;
        margin: 10px 0;
        color: #a020f0;
    }
    
    /* Form controls */
    div[data-baseweb="select"] > div {
        background-color: #121212 !important;
        border-color: #333 !important;
        color: white !important;
    }
    
    div[data-baseweb="input"] > div {
        background-color: #121212 !important;
        border-color: #333 !important;
        color: white !important;
    }
    
    div[data-baseweb="checkbox"] {
        color: white !important;
    }
    
    /* Improve sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #121212;
    }
    
    section[data-testid="stSidebar"] h1 {
        color: #a020f0 !important;
    }
    
    section[data-testid="stSidebar"] p {
        color: white !important;
    }
    
    /* Fix radio button styling */
    .stRadio label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books'")
    if not cursor.fetchone():
        cursor.execute('''
        CREATE TABLE books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publication_year INTEGER,
            genre TEXT,
            read_status INTEGER,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
    else:
        try:
            cursor.execute("SELECT read_status FROM books LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE books ADD COLUMN read_status INTEGER DEFAULT 0")
            conn.commit()
    
    return conn

def add_book(conn, title, author, publication_year, genre, read_status):
    cursor = conn.cursor()
    try:
        read_status_int = 1 if read_status else 0
        cursor.execute('''
        INSERT INTO books (title, author, publication_year, genre, read_status)
        VALUES (?, ?, ?, ?, ?)
        ''', (title, author, publication_year, genre, read_status_int))
        conn.commit()
        return True
    except sqlite3.Error:
        return False

def remove_book_by_title(conn, title):
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE title = ?", (title,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        return False

def search_books(conn, search_term, search_by):
    cursor = conn.cursor()
    try:
        query = f"SELECT * FROM books WHERE {search_by} LIKE ?"
        cursor.execute(query, (f'%{search_term}%',))
        return cursor.fetchall()
    except sqlite3.Error:
        return []

def get_all_books(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM books")
        return cursor.fetchall()
    except sqlite3.Error:
        return []

def get_statistics(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM books")
        total_books = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM books WHERE read_status = 1")
        read_books = cursor.fetchone()[0]
        
        percentage_read = 0
        if total_books > 0:
            percentage_read = (read_books / total_books) * 100
        
        return total_books, read_books, percentage_read
    except sqlite3.Error:
        return 0, 0, 0

conn = init_db()

def get_column_names(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(books)")
        columns = cursor.fetchall()
        return [col[1] for col in columns]
    except sqlite3.Error:
        return ["ID", "Title", "Author", "Publication Year", "Genre", "Read Status", "Date Added"]

column_names = get_column_names(conn)

def display_book_card(book, cols):
    with cols[0]:
        read_status_text = "Read" if book['read_status'] else "Unread"
        status_class = "status-read" if book['read_status'] else "status-unread"
        st.markdown(f"""
        <div class="book-card">
            <h3>{book['title']}</h3>
            <p><strong>by {book['author']}</strong></p>
            <p>Year: {book['publication_year']} | Genre: {book['genre']}</p>
            <p>Status: <span class="{status_class}">{read_status_text}</span></p>
        </div>
        """, unsafe_allow_html=True)

st.sidebar.title("Library Manager")
st.sidebar.write("📚 Your Personal Collection")

page_icons = {
    "Home": "🏠",
    "Add Book": "➕",
    "Remove Book": "🗑️",
    "Search Books": "🔍",
    "View All Books": "📋",
    "Statistics": "📊"
}

page = st.sidebar.radio("", list(page_icons.keys()), format_func=lambda x: f"{page_icons[x]} {x}")

if page == "Home":
    st.title("📚 Personal Library Manager")
    
    st.markdown("""
    <div class="simple-card">
        <h2>Welcome to your Personal Library Manager!</h2>
        <p>Track, organize, and discover your collection.</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_books, read_books, percentage_read = get_statistics(conn)
    
    st.subheader("Quick Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Books</h3>
            <p>{}</p>
        </div>
        """.format(total_books), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Books Read</h3>
            <p>{}</p>
        </div>
        """.format(read_books), unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Progress</h3>
            <p>{:.1f}%</p>
        </div>
        """.format(percentage_read), unsafe_allow_html=True)
    
    st.subheader("Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="simple-card">
            <h3>Manage Your Collection</h3>
            <ul>
                <li>Add new books to your library</li>
                <li>Remove books you no longer own</li>
                <li>Keep track of reading status</li>
                <li>Organize by genre and author</li>
            </ul>
       </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="simple-card">
            <h3>Discover Insights</h3>
            <ul>
                <li>Track reading progress</li>
                <li>Visualize genre distribution</li>
                <li>Identify your favorite authors</li>
                <li>Analyze publication years</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    if total_books > 0:
        st.subheader("Recent Additions")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM books ORDER BY date_added DESC LIMIT 3")
        recent_books = cursor.fetchall()
        
        if recent_books:
            df = pd.DataFrame(recent_books, columns=column_names)
            df["read_status"] = df["read_status"].apply(lambda x: "Read" if x else "Unread")
            
            cols = st.columns(3)
            for i, (_, book) in enumerate(df.iterrows()):
                book_dict = book.to_dict()
                display_book_card(book_dict, [cols[i % 3]])

elif page == "Add Book":
    st.title("Add a New Book")
    
    st.markdown("""
    <div class="simple-card">
        <p>Add books to your personal collection by filling out the form below.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("add_book_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            genre = st.text_input("Genre")
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, value=2023)
            read_status = st.checkbox("Have you read this book?")
        
        submitted = st.form_submit_button("Add Book")
        
        if submitted:
            if title and author and genre:
                if add_book(conn, title, author, publication_year, genre, read_status):
                    st.success("Book added successfully to your collection.")
                else:
                    st.error("Failed to add book. Please try again.")
            else:
                st.warning("Please provide all fields.")

elif page == "Remove Book":
    st.title("Remove a Book")
    
    st.markdown("""
    <div class="simple-card">
        <p>Select a book to remove from your collection.</p>
    </div>
    """, unsafe_allow_html=True)
    
    books = get_all_books(conn)
    
    if not books:
        st.info("Your library is empty. Add some books to get started!")
    else:
        df = pd.DataFrame(books, columns=column_names)
        
        if "read_status" in df.columns:
            df["read_status"] = df["read_status"].apply(lambda x: "Read" if x else "Unread")
        
        book_titles = df["title"].tolist()
        
        st.subheader("Select a Book to Remove")
        selected_book = st.selectbox("Choose a book to remove", book_titles)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            remove_button = st.button("Remove Selected Book")
        
        if remove_button:
            if remove_book_by_title(conn, selected_book):
                st.success(f'"{selected_book}" has been removed from your collection.')
                st.rerun()
            else:
                st.error(f"Failed to remove book.")

elif page == "Search Books":
    st.title("Search for Books")
    
    st.markdown("""
    <div class="simple-card">
        <p>Find books in your collection by title, author, or genre.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        search_by = st.radio("Search by", ["Title", "Author", "Genre"])
    
    with col2:
        search_term = st.text_input("Enter search term", placeholder="Type here to search...")
        search_button = st.button("Search")
    
    if search_term and search_button:
        results = search_books(conn, search_term, search_by)
        
        if results:
            st.success(f"Found {len(results)} matching books")
            
            df = pd.DataFrame(results, columns=column_names)
            
            if "read_status" in df.columns:
                df["read_status"] = df["read_status"].apply(lambda x: "Read" if x else "Unread")
            
            display_columns = [col for col in ["title", "author", "publication_year", "genre", "read_status"] if col in df.columns]
            filtered_df = df[display_columns]
            num_cols = 3
            rows = (len(filtered_df) + num_cols - 1) // num_cols
            
            for i in range(rows):
                cols = st.columns(num_cols)
                for j in range(num_cols):
                    idx = i * num_cols + j
                    if idx < len(filtered_df):
                        book_dict = df.iloc[idx].to_dict()
                        display_book_card(book_dict, [cols[j]])
        else:
            st.info(f"No books match your search for '{search_term}' in {search_by}.")

elif page == "View All Books":
    st.title("All Books in Your Library")
    
    books = get_all_books(conn)
    
    if not books:
        st.info("Your library is empty. Start by adding some books!")
    else:
        df = pd.DataFrame(books, columns=column_names)
        
        if "read_status" in df.columns:
            df["read_status"] = df["read_status"].apply(lambda x: "Read" if x else "Unread")
        
        st.subheader("Filter and Sort")
        
        col1, col2 = st.columns(2)
        with col1:
            all_genres = list(df["genre"].unique()) if "genre" in df.columns else []
            genre_filter = st.multiselect("Filter by Genre", options=all_genres if all_genres else ["No genres available"])
        with col2:
            sort_columns = [col for col in ["title", "author", "publication_year", "genre"] if col in df.columns]
            sort_labels = [col.replace('_', ' ').title() for col in sort_columns]
            sort_dict = dict(zip(sort_labels, sort_columns))
            
            sort_by_label = st.selectbox("Sort by", sort_labels if sort_labels else ["No options available"])
            sort_by = sort_dict.get(sort_by_label, sort_labels[0] if sort_labels else None)
        
        filtered_df = df
        if genre_filter and all_genres and "genre" in df.columns:
            filtered_df = filtered_df[filtered_df["genre"].isin(genre_filter)]
        
        if sort_by in df.columns:
            filtered_df = filtered_df.sort_values(by=sort_by)
        
        st.success(f"Showing {len(filtered_df)} books")
        
        display_columns = [col for col in ["title", "author", "publication_year", "genre", "read_status"] if col in filtered_df.columns]
        
        num_cols = 3
        rows = (len(filtered_df) + num_cols - 1) // num_cols
        
        for i in range(rows):
            cols = st.columns(num_cols)
            for j in range(num_cols):
                idx = i * num_cols + j
                if idx < len(filtered_df):
                    book_dict = filtered_df.iloc[idx].to_dict()
                    display_book_card(book_dict, [cols[j]])
        
        show_table = st.checkbox("Show as table instead")
        if show_table:
            st.dataframe(filtered_df[display_columns])

elif page == "Statistics":
    st.title("Library Statistics")
    
    st.markdown("""
    <div class="simple-card">
        <p>Get insights about your book collection.</p>
    </div>
    """, unsafe_allow_html=True)
    
    total_books, read_books, percentage_read = get_statistics(conn)
    
    if total_books == 0:
        st.info("Your library is empty. Add some books to see statistics!")
    else:
        st.subheader("Reading Progress")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>Total Books</h3>
                <p>{}</p>
            </div>
            """.format(total_books), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>Books Read</h3>
                <p>{}</p>
            </div>
            """.format(read_books), unsafe_allow_html=True)
            
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>Progress</h3>
                <p>{:.1f}%</p>
            </div>
            """.format(percentage_read), unsafe_allow_html=True)
        
        books = get_all_books(conn)
        df = pd.DataFrame(books, columns=column_names)
        
        if "genre" in df.columns:
            st.subheader("Genre Distribution")
            genre_counts = df["genre"].value_counts()
            
            st.bar_chart(genre_counts)
            
            most_common_genre = genre_counts.idxmax()
            st.markdown(f"""
            <div class="simple-card">
                <p>Your most common genre is <strong>{most_common_genre}</strong> with <strong>{genre_counts[most_common_genre]}</strong> books.</p>
            </div>
            """, unsafe_allow_html=True)
        
        if "publication_year" in df.columns:
            st.subheader("Publication Years")
            
            year_min = int(df["publication_year"].min())
            year_max = int(df["publication_year"].max())
            
            decade_start = (year_min // 10) * 10
            decade_end = ((year_max // 10) + 1) * 10
            decades = range(decade_start, decade_end, 10)
            
            df["decade"] = df["publication_year"].apply(lambda x: (x // 10) * 10)
            decade_counts = df["decade"].value_counts().sort_index()
            
            st.line_chart(decade_counts)
            
            if not df.empty:
                oldest_book = df.loc[df["publication_year"].idxmin()]
                newest_book = df.loc[df["publication_year"].idxmax()]
                
                st.markdown(f"""
                <div class="simple-card">
                    <p>Your oldest book is <strong>{oldest_book['title']}</strong> ({oldest_book['publication_year']}) by {oldest_book['author']}.</p>
                    <p>Your newest book is <strong>{newest_book['title']}</strong> ({newest_book['publication_year']}) by {newest_book['author']}.</p>
                </div>
                """, unsafe_allow_html=True)
        
        if "author" in df.columns:
            st.subheader("Author Breakdown")
            
            author_counts = df["author"].value_counts()
            top_authors = author_counts.head(5)
            
            st.markdown("""
            <div class="simple-card">
                <h3>Top Authors</h3>
            """, unsafe_allow_html=True)
            
            for author, count in top_authors.items():
                st.markdown(f"- <strong>{author}</strong>: {count} books", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            if "read_status" in df.columns:
                read_books_df = df[df["read_status"] == 1]
                if not read_books_df.empty:
                    read_author_counts = read_books_df["author"].value_counts()
                    if not read_author_counts.empty:
                        most_read_author = read_author_counts.idxmax()
                        st.markdown(f"""
                        <div class="simple-card">
                            <p>You've read the most books by <strong>{most_read_author}</strong> ({read_author_counts[most_read_author]} books).</p>
                        </div>
                        """, unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.info("Developed By Wania Azam")

