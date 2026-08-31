# Seed data for StreamPicker OTT discovery engine

PROVIDERS_DATA = [
    {
        "id": "netflix",
        "name": "Netflix",
        "icon_url": "https://assets.nflxext.com/ffe/siteui/common/icons/monogram/netflix-logo-square.png",
        "brand_color": "#E50914",
        "badge_bg": "rgba(229, 9, 20, 0.15)",
        "monthly_price_inr": 199.0,
        "display_priority": 1,
    },
    {
        "id": "prime_video",
        "name": "Amazon Prime Video",
        "icon_url": "https://m.media-amazon.com/images/G/01/digital/video/web/logo-min-remake.png",
        "brand_color": "#00A8E1",
        "badge_bg": "rgba(0, 168, 225, 0.15)",
        "monthly_price_inr": 299.0,
        "display_priority": 2,
    },
    {
        "id": "hotstar",
        "name": "Disney+ Hotstar",
        "icon_url": "https://secure-media.hotstar.com/static/hotstar-logo.png",
        "brand_color": "#113CCF",
        "badge_bg": "rgba(17, 60, 207, 0.15)",
        "monthly_price_inr": 299.0,
        "display_priority": 3,
    },
    {
        "id": "apple_tv",
        "name": "Apple TV+",
        "icon_url": "https://www.apple.com/v/apple-tv-plus/ah/images/meta/apple-tv__e60wf2v1k4ia_og.png",
        "brand_color": "#A2AAAD",
        "badge_bg": "rgba(162, 170, 173, 0.15)",
        "monthly_price_inr": 99.0,
        "display_priority": 4,
    },
    {
        "id": "sonyliv",
        "name": "SonyLIV",
        "icon_url": "https://images.slivcdn.com/UI_icons/sonyliv_new_revised_header_logo.png",
        "brand_color": "#0099FF",
        "badge_bg": "rgba(0, 153, 255, 0.15)",
        "monthly_price_inr": 299.0,
        "display_priority": 6,
    },
    {
        "id": "zee5",
        "name": "ZEE5",
        "icon_url": "https://www.zee5.com/images/ZEE5_logo.svg",
        "brand_color": "#8230C6",
        "badge_bg": "rgba(130, 48, 198, 0.15)",
        "monthly_price_inr": 149.0,
        "display_priority": 7,
    }
]

TITLES_DATA = [
    {
        "tmdb_id": "872585",
        "imdb_id": "tt15398776",
        "title": "Oppenheimer",
        "type": "movie",
        "runtime_minutes": 180,
        "release_year": 2023,
        "genres": "Biography, Drama, History, Thriller",
        "mood_tags": "Mind-Bending, Intense Drama, Cerebral, Dark & Gritty",
        "director": "Christopher Nolan",
        "cast_members": "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr., Florence Pugh",
        "rating_imdb": 8.9,
        "rating_tmdb": 8.1,
        "rating_rotten_tomatoes": 93,
        "overview": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during the Manhattan Project.",
        "poster_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=uYPbbksJxIg",
        "providers": [
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/movies/oppenheimer/1260161499",
                "deep_link": "hotstar://movies/1260161499"
            },
            {
                "provider_id": "prime_video",
                "access_type": "rent",
                "price": 149.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Oppenheimer/0NQJ6L6K",
                "deep_link": "primevideo://detail?asin=B0CGV2X5Z8"
            }
        ]
    },
    {
        "tmdb_id": "27205",
        "imdb_id": "tt1375666",
        "title": "Inception",
        "type": "movie",
        "runtime_minutes": 148,
        "release_year": 2010,
        "genres": "Action, Sci-Fi, Adventure, Thriller",
        "mood_tags": "Mind-Bending, Adrenaline Rush, Cerebral, Suspense",
        "director": "Christopher Nolan",
        "cast_members": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page, Tom Hardy, Ken Watanabe",
        "rating_imdb": 8.8,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 87,
        "overview": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "poster_url": "https://image.tmdb.org/t/p/w500/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/70131314",
                "deep_link": "nflx://title/70131314"
            },
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Inception/0I7C58O4",
                "deep_link": "primevideo://detail?asin=B003VWCX12"
            }
        ]
    },
    {
        "tmdb_id": "157336",
        "imdb_id": "tt0816692",
        "title": "Interstellar",
        "type": "movie",
        "runtime_minutes": 169,
        "release_year": 2014,
        "genres": "Adventure, Drama, Sci-Fi",
        "mood_tags": "Mind-Bending, Emotional, Cerebral, Epic Scope",
        "director": "Christopher Nolan",
        "cast_members": "Matthew McConaughey, Anne Hathaway, Jessica Chastain, Michael Caine",
        "rating_imdb": 8.7,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 73,
        "overview": "When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans.",
        "poster_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Interstellar/0K8C7U91",
                "deep_link": "primevideo://detail?asin=B00TX7O123"
            }
        ]
    },
    {
        "tmdb_id": "545611",
        "imdb_id": "tt7286456",
        "title": "Everything Everywhere All at Once",
        "type": "movie",
        "runtime_minutes": 139,
        "release_year": 2022,
        "genres": "Action, Adventure, Comedy, Sci-Fi",
        "mood_tags": "Mind-Bending, Feel-Good & Uplifting, Absurdist, Adrenaline Rush",
        "director": "Daniel Kwan, Daniel Scheinert",
        "cast_members": "Michelle Yeoh, Stephanie Hsu, Ke Huy Quan, Jamie Lee Curtis",
        "rating_imdb": 7.8,
        "rating_tmdb": 7.8,
        "rating_rotten_tomatoes": 94,
        "overview": "A middle-aged Chinese immigrant is swept up into an insane adventure in which she alone can save existence by exploring other universes and connecting with the lives she could have led.",
        "poster_url": "https://image.tmdb.org/t/p/w500/w3LxiVYPq6ABGNO9FYmuipEIb57.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/7ZO959VEQL7Pp1nqe9kO1kXv9q1.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=wxN1T1ux128",
        "providers": [
            {
                "provider_id": "sonyliv",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.sonyliv.com/movies/everything-everywhere-all-at-once-100018902",
                "deep_link": "sonyliv://content/movie/100018902"
            }
        ]
    },
    {
        "tmdb_id": "220289",
        "imdb_id": "tt2866360",
        "title": "Coherence",
        "type": "movie",
        "runtime_minutes": 89,
        "release_year": 2013,
        "genres": "Mystery, Sci-Fi, Thriller",
        "mood_tags": "Mind-Bending, Late-Night Mystery, Cerebral, Quick Watch",
        "director": "James Ward Byrkit",
        "cast_members": "Emily Baldoni, Maury Sterling, Nicholas Brendon, Elizabeth Gracen",
        "rating_imdb": 7.2,
        "rating_tmdb": 7.3,
        "rating_rotten_tomatoes": 88,
        "overview": "Strange things begin to happen when a group of eight friends gather for a dinner party on an evening when an astrological comet is passing overhead.",
        "poster_url": "https://image.tmdb.org/t/p/w500/l0p3Yk39yJb89R9V3XWqQ9r18f8.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/1k1qP108eYp8n138v2K9A.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=sEceDz11tw8",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Coherence/0I9A7P41",
                "deep_link": "primevideo://detail?asin=B00I3MVW7S"
            }
        ]
    },
    {
        "tmdb_id": "118340",
        "imdb_id": "tt1853728",
        "title": "Guardians of the Galaxy",
        "type": "movie",
        "runtime_minutes": 121,
        "release_year": 2014,
        "genres": "Action, Adventure, Comedy, Sci-Fi",
        "mood_tags": "Feel-Good & Uplifting, Adrenaline Rush, Hilarious Comedy, Fun",
        "director": "James Gunn",
        "cast_members": "Chris Pratt, Zoe Saldana, Dave Bautista, Vin Diesel, Bradley Cooper",
        "rating_imdb": 8.0,
        "rating_tmdb": 7.9,
        "rating_rotten_tomatoes": 92,
        "overview": "A group of intergalactic criminals must pull together to stop a fanatical warrior with plans to purge the universe.",
        "poster_url": "https://image.tmdb.org/t/p/w500/r7vmZjiyZw9rpJMQJdXpjgiCOk9.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/uLtV5o55UySV12Y1muEZqq294r.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=d96cjJhvlMA",
        "providers": [
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/movies/guardians-of-the-galaxy/1260018302",
                "deep_link": "hotstar://movies/1260018302"
            }
        ]
    },
    {
        "tmdb_id": "496243",
        "imdb_id": "tt6751668",
        "title": "Parasite",
        "type": "movie",
        "runtime_minutes": 132,
        "release_year": 2019,
        "genres": "Comedy, Drama, Thriller",
        "mood_tags": "Mind-Bending, Dark & Gritty, Suspense, Masterpiece",
        "director": "Bong Joon-ho",
        "cast_members": "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong, Choi Woo-shik, Park So-dam",
        "rating_imdb": 8.5,
        "rating_tmdb": 8.5,
        "rating_rotten_tomatoes": 99,
        "overview": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/hiKmpZMGZsrkA3cdEvuyeqaBTqq.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=5xH0hhTEb8E",
        "providers": [
            {
                "provider_id": "sonyliv",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.sonyliv.com/movies/parasite-1000004921",
                "deep_link": "sonyliv://content/movie/1000004921"
            }
        ]
    },
    {
        "tmdb_id": "374720",
        "imdb_id": "tt4422836",
        "title": "Dunkirk",
        "type": "movie",
        "runtime_minutes": 106,
        "release_year": 2017,
        "genres": "Action, Drama, History, War",
        "mood_tags": "Adrenaline Rush, Suspense, Intense Drama, Fast Paced",
        "director": "Christopher Nolan",
        "cast_members": "Fionn Whitehead, Barry Keoghan, Mark Rylance, Tom Hardy, Cillian Murphy",
        "rating_imdb": 7.8,
        "rating_tmdb": 7.5,
        "rating_rotten_tomatoes": 92,
        "overview": "Allied soldiers from Belgium, the British Empire, and France are surrounded by the German Army and evacuated during a fierce battle in World War II.",
        "poster_url": "https://image.tmdb.org/t/p/w500/ebSnODDg9lbsMIaWg2uAbjn7TO5.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/fudEG1VUWuOqleXv6NwCExK0VLy.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=F-eMt3SrfFU",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/80170278",
                "deep_link": "nflx://title/80170278"
            },
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Dunkirk/0GQ3P472",
                "deep_link": "primevideo://detail?asin=B0748F7HJW"
            }
        ]
    },
    {
        "tmdb_id": "335984",
        "imdb_id": "tt1856101",
        "title": "Blade Runner 2049",
        "type": "movie",
        "runtime_minutes": 164,
        "release_year": 2017,
        "genres": "Action, Drama, Mystery, Sci-Fi, Thriller",
        "mood_tags": "Mind-Bending, Dark & Gritty, Cerebral Sci-Fi, Atmospheric",
        "director": "Denis Villeneuve",
        "cast_members": "Ryan Gosling, Harrison Ford, Ana de Armas, Sylvia Hoeks, Robin Wright",
        "rating_imdb": 8.0,
        "rating_tmdb": 7.6,
        "rating_rotten_tomatoes": 88,
        "overview": "Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard, who's been missing for thirty years.",
        "poster_url": "https://image.tmdb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/ilRyAZVAQ0wQpP9hY9vA5M3m5l3.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=gCcx85zbxz4",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/80185760",
                "deep_link": "nflx://title/80185760"
            },
            {
                "provider_id": "sonyliv",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.sonyliv.com/movies/blade-runner-2049-1000003011",
                "deep_link": "sonyliv://content/movie/1000003011"
            }
        ]
    },
    {
        "tmdb_id": "438631",
        "imdb_id": "tt6710474",
        "title": "Dune",
        "type": "movie",
        "runtime_minutes": 155,
        "release_year": 2021,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "mood_tags": "Epic Scope, Cerebral Sci-Fi, Atmospheric, Intense Drama",
        "director": "Denis Villeneuve",
        "cast_members": "Timothée Chalamet, Rebecca Ferguson, Oscar Isaac, Josh Brolin, Zendaya",
        "rating_imdb": 8.0,
        "rating_tmdb": 7.8,
        "rating_rotten_tomatoes": 83,
        "overview": "Paul Atreides, a brilliant and gifted young man born into a great destiny beyond his understanding, must travel to the most dangerous planet in the universe to ensure the future of his family and his people.",
        "poster_url": "https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/jYEW5xZkZk2WTrdbMGAPFuBqbDc.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=n9xhJrPXop4",
        "providers": [
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/movies/dune/1260161477",
                "deep_link": "hotstar://movies/1260161477"
            },
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Dune/0Q9T418B",
                "deep_link": "primevideo://detail?asin=B09HX5F1P2"
            }
        ]
    },
    {
        "tmdb_id": "693134",
        "imdb_id": "tt15239678",
        "title": "Dune: Part Two",
        "type": "movie",
        "runtime_minutes": 166,
        "release_year": 2024,
        "genres": "Action, Adventure, Drama, Sci-Fi",
        "mood_tags": "Epic Scope, Adrenaline Rush, Masterpiece, Mind-Bending",
        "director": "Denis Villeneuve",
        "cast_members": "Timothée Chalamet, Zendaya, Rebecca Ferguson, Javier Bardem, Austin Butler",
        "rating_imdb": 8.6,
        "rating_tmdb": 8.2,
        "rating_rotten_tomatoes": 92,
        "overview": "Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family.",
        "poster_url": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/xOMo8BRK7PfcJv9JCnx7s520QIe.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=Way9Dexny3w",
        "providers": [
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/movies/dune-part-two/1260161488",
                "deep_link": "hotstar://movies/1260161488"
            },
            {
                "provider_id": "apple_tv",
                "access_type": "rent",
                "price": 149.0,
                "currency": "INR",
                "web_url": "https://tv.apple.com/in/movie/dune-part-two/umc.cmc.3o7eecdf61q",
                "deep_link": "appletv://movie/dune-part-two"
            }
        ]
    },
    {
        "tmdb_id": "313369",
        "imdb_id": "tt3315342",
        "title": "La La Land",
        "type": "movie",
        "runtime_minutes": 128,
        "release_year": 2016,
        "genres": "Comedy, Drama, Music, Romance",
        "mood_tags": "Date Night, Feel-Good & Uplifting, Emotional, Melancholic",
        "director": "Damien Chazelle",
        "cast_members": "Ryan Gosling, Emma Stone, John Legend, J.K. Simmons",
        "rating_imdb": 8.0,
        "rating_tmdb": 7.9,
        "rating_rotten_tomatoes": 91,
        "overview": "While navigating their careers in Los Angeles, a pianist and an actress fall in love while attempting to reconcile their aspirations for the future.",
        "poster_url": "https://image.tmdb.org/t/p/w500/uDO8zWDhfWwoFdKS4fzkVJt0Rf0.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/qJeU7KM4o6mK9gY7Uf1iC9s4iQ7.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=0pdqf4P9MB8",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/La-La-Land/0GQ3P472",
                "deep_link": "primevideo://detail?asin=B01MRX4L90"
            },
            {
                "provider_id": "lionsgateplay",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/La-La-Land/0GQ3P472",
                "deep_link": "primevideo://detail?asin=B01MRX4L90"
            }
        ]
    },
    {
        "tmdb_id": "244786",
        "imdb_id": "tt2582802",
        "title": "Whiplash",
        "type": "movie",
        "runtime_minutes": 107,
        "release_year": 2014,
        "genres": "Drama, Music",
        "mood_tags": "Adrenaline Rush, Intense Drama, Dark & Gritty, Fast Paced",
        "director": "Damien Chazelle",
        "cast_members": "Miles Teller, J.K. Simmons, Paul Reiser, Melissa Benoist",
        "rating_imdb": 8.5,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 94,
        "overview": "A promising young drummer enrolls at a cut-throat music conservatory where his dreams of greatness are mentored by an instructor who will stop at nothing to realize a student's potential.",
        "poster_url": "https://image.tmdb.org/t/p/w500/7fn624j5lj3xTme2SgiLCeuedmO.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/6bbZ6XUwvgfIhYstcwaV6fBPYZH.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=7d_jQycdQGo",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/70299275",
                "deep_link": "nflx://title/70299275"
            },
            {
                "provider_id": "sonyliv",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.sonyliv.com/movies/whiplash-1000002938",
                "deep_link": "sonyliv://content/movie/1000002938"
            }
        ]
    },
    {
        "tmdb_id": "550",
        "imdb_id": "tt0137523",
        "title": "Fight Club",
        "type": "movie",
        "runtime_minutes": 139,
        "release_year": 1999,
        "genres": "Drama",
        "mood_tags": "Mind-Bending, Dark & Gritty, Cult Classic, Cerebral",
        "director": "David Fincher",
        "cast_members": "Brad Pitt, Edward Norton, Helena Bonham Carter, Meat Loaf",
        "rating_imdb": 8.8,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 79,
        "overview": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
        "poster_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/hZkgoQYus5vegHoetLkCJzb17zJ.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=qtRKDV93Mt8",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Fight-Club/0HQ4G19P",
                "deep_link": "primevideo://detail?asin=B001TKO91Q"
            },
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/movies/fight-club/1770000923",
                "deep_link": "hotstar://movies/1770000923"
            }
        ]
    },
    {
        "tmdb_id": "19404",
        "imdb_id": "tt0113277",
        "title": "Dilwale Dulhania Le Jayenge",
        "type": "movie",
        "runtime_minutes": 189,
        "release_year": 1995,
        "genres": "Drama, Romance",
        "mood_tags": "Date Night, Feel-Good & Uplifting, Comfort Watch, Iconic Classic",
        "director": "Aditya Chopra",
        "cast_members": "Shah Rukh Khan, Kajol, Amrish Puri, Anupam Kher",
        "rating_imdb": 8.0,
        "rating_tmdb": 8.6,
        "rating_rotten_tomatoes": 100,
        "overview": "When Raj meets Simran in Europe, it isn't love at first sight but when Simran moves to India for an arranged marriage, love takes over.",
        "poster_url": "https://image.tmdb.org/t/p/w500/ktejodb090x6q3g0rP9rOQ2VwT9.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/90A4LzXm6t10r3p7PqO.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=c25GKl5VNeY",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Dilwale-Dulhania-Le-Jayenge/0O84T5G1",
                "deep_link": "primevideo://detail?asin=B07N8G6P3Q"
            }
        ]
    },
    {
        "tmdb_id": "20453",
        "imdb_id": "tt1187043",
        "title": "3 Idiots",
        "type": "movie",
        "runtime_minutes": 170,
        "release_year": 2009,
        "genres": "Comedy, Drama",
        "mood_tags": "Feel-Good & Uplifting, Hilarious Comedy, Emotional, Comfort Watch",
        "director": "Rajkumar Hirani",
        "cast_members": "Aamir Khan, R. Madhavan, Sharman Joshi, Kareena Kapoor, Boman Irani",
        "rating_imdb": 8.4,
        "rating_tmdb": 8.0,
        "rating_rotten_tomatoes": 100,
        "overview": "Two friends are searching for their long lost companion. They revisit their college days and recall the memories of their friend who inspired them to think differently.",
        "poster_url": "https://image.tmdb.org/t/p/w500/66A9MqXOyVFCssoloscw79z89ew.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/u7kuU3V0Q8vH07t2V9Pq1.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=K0eDlFX9GMc",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/3-Idiots/0J83B4P1",
                "deep_link": "primevideo://detail?asin=B07N9D8V2Q"
            }
        ]
    },
    {
        "tmdb_id": "787699",
        "imdb_id": "tt1087461",
        "title": "12th Fail",
        "type": "movie",
        "runtime_minutes": 147,
        "release_year": 2023,
        "genres": "Biography, Drama",
        "mood_tags": "Feel-Good & Uplifting, Emotional, Inspiring, Realistic",
        "director": "Vidhu Vinod Chopra",
        "cast_members": "Vikrant Massey, Medha Shankr, Anant V Joshi, Anshumaan Pushkar",
        "rating_imdb": 8.9,
        "rating_tmdb": 8.3,
        "rating_rotten_tomatoes": 91,
        "overview": "Based on the true story of IPS officer Manoj Kumar Sharma, 12th Fail tells the story of how Manoj braved severe poverty and failure to restart his academic journey and achieve his dreams.",
        "poster_url": "https://image.tmdb.org/t/p/w500/y4v8O0L360jX73V8bO1.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/9i0p1t0v9a38k20f83h.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=we33aV33t8A",
        "providers": [
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/movies/12th-fail/1260161474",
                "deep_link": "hotstar://movies/1260161474"
            }
        ]
    },
    {
        "tmdb_id": "603",
        "imdb_id": "tt0133093",
        "title": "The Matrix",
        "type": "movie",
        "runtime_minutes": 136,
        "release_year": 1999,
        "genres": "Action, Sci-Fi",
        "mood_tags": "Mind-Bending, Adrenaline Rush, Cerebral Sci-Fi, Cult Classic",
        "director": "Lana Wachowski, Lilly Wachowski",
        "cast_members": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss, Hugo Weaving",
        "rating_imdb": 8.7,
        "rating_tmdb": 8.2,
        "rating_rotten_tomatoes": 83,
        "overview": "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
        "poster_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/l4QHerTSbMI7qgvej05APLIPwJ3.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/20557937",
                "deep_link": "nflx://title/20557937"
            },
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/The-Matrix/0M7B4P10",
                "deep_link": "primevideo://detail?asin=B000HB3P5Q"
            }
        ]
    },
    {
        "tmdb_id": "1396",
        "imdb_id": "tt0903747",
        "title": "Breaking Bad",
        "type": "series",
        "runtime_minutes": 47,
        "release_year": 2008,
        "genres": "Crime, Drama, Thriller",
        "mood_tags": "Dark & Gritty, Intense Drama, Masterpiece, High-Stakes Action",
        "director": "Vince Gilligan",
        "cast_members": "Bryan Cranston, Aaron Paul, Anna Gunn, Dean Norris, Betsy Brandt",
        "rating_imdb": 9.5,
        "rating_tmdb": 8.9,
        "rating_rotten_tomatoes": 96,
        "overview": "A chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine with a former student in order to secure his family's future.",
        "poster_url": "https://image.tmdb.org/t/p/w500/ztkUQFLlC19CCMYHW9o1zWhJRNq.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/tsRy63Mu5cu8etL1X7ZLyf7UP1M.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=HhesaQXLuRY",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/70143836",
                "deep_link": "nflx://title/70143836"
            }
        ]
    },
    {
        "tmdb_id": "94605",
        "imdb_id": "tt11280740",
        "title": "Severance",
        "type": "series",
        "runtime_minutes": 55,
        "release_year": 2022,
        "genres": "Drama, Mystery, Sci-Fi, Thriller",
        "mood_tags": "Mind-Bending, Late-Night Mystery, Cerebral Sci-Fi, Dark & Gritty",
        "director": "Ben Stiller, Aoife McArdle",
        "cast_members": "Adam Scott, Zach Cherry, Britt Lower, Patricia Arquette, John Turturro, Christopher Walken",
        "rating_imdb": 8.7,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 97,
        "overview": "Mark leads a team of office workers whose memories have been surgically divided between their work and personal lives. When a mysterious colleague appears outside of work, it begins a journey to discover the truth about their jobs.",
        "poster_url": "https://image.tmdb.org/t/p/w500/pPH9w9DE5vY7g0P2t1r8b3g9p1.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/1k1qP108eYp8n138v2K9A.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=xEQP4VVuyrY",
        "providers": [
            {
                "provider_id": "apple_tv",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://tv.apple.com/in/show/severance/umc.cmc.1srk2goyh2q2zpalkqnj6ogm4",
                "deep_link": "appletv://show/severance"
            }
        ]
    },
    {
        "tmdb_id": "119051",
        "imdb_id": "tt11198330",
        "title": "Wednesday",
        "type": "series",
        "runtime_minutes": 50,
        "release_year": 2022,
        "genres": "Comedy, Crime, Fantasy, Mystery",
        "mood_tags": "Late-Night Mystery, Fun, Dark Comedy, Teen Drama",
        "director": "Tim Burton",
        "cast_members": "Jenna Ortega, Gwendoline Christie, Riki Lindhome, Jamie McShane",
        "rating_imdb": 8.1,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 72,
        "overview": "A sleuthing, supernaturally infused mystery charting Wednesday Addams' years as a student at Nevermore Academy.",
        "poster_url": "https://image.tmdb.org/t/p/w500/9PFonQ9dcSlOGTTVv2R97AcSTTr.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/iHSwvRVsRyxpX7FE7GbviaDvgGZ.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=Di310BC8BpY",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/81231974",
                "deep_link": "nflx://title/81231974"
            }
        ]
    },
    {
        "tmdb_id": "82856",
        "imdb_id": "tt8111088",
        "title": "The Mandalorian",
        "type": "series",
        "runtime_minutes": 40,
        "release_year": 2019,
        "genres": "Action, Adventure, Sci-Fi",
        "mood_tags": "Adrenaline Rush, Feel-Good & Uplifting, Epic Scope, Quick Watch",
        "director": "Jon Favreau",
        "cast_members": "Pedro Pascal, Carl Weathers, Giancarlo Esposito, Katee Sackhoff",
        "rating_imdb": 8.6,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 90,
        "overview": "After the defeat of the Galactic Empire, a lone bounty hunter makes his way through the outer reaches of the lawless galaxy.",
        "poster_url": "https://image.tmdb.org/t/p/w500/eU1i6eHXlzMOlEq0ku1R07Y87Ni.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/o76ZDm8PS9791XKL2YehUmOheo1.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=aOC8E8R_N5c",
        "providers": [
            {
                "provider_id": "hotstar",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.hotstar.com/in/shows/the-mandalorian/1260021071",
                "deep_link": "hotstar://shows/1260021071"
            }
        ]
    },
    {
        "tmdb_id": "114472",
        "imdb_id": "tt10857164",
        "title": "Panchayat",
        "type": "series",
        "runtime_minutes": 35,
        "release_year": 2020,
        "genres": "Comedy, Drama",
        "mood_tags": "Feel-Good & Uplifting, Comfort Watch, Hilarious Comedy, Quick Watch",
        "director": "Deepak Kumar Mishra",
        "cast_members": "Jitendra Kumar, Neena Gupta, Raghubir Yadav, Chandan Roy, Faisal Malik",
        "rating_imdb": 8.9,
        "rating_tmdb": 8.4,
        "rating_rotten_tomatoes": 95,
        "overview": "A comedy-drama, which captures the journey of an engineering graduate Abhishek, who for lack of a better job option joins as secretary of a Panchayat office in a remote village of Uttar Pradesh.",
        "poster_url": "https://image.tmdb.org/t/p/w500/k2t2a3b0q19r8b3g9p1.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/8t0q18h38a0k27t1.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=mojZJ7oeD_g",
        "providers": [
            {
                "provider_id": "prime_video",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.primevideo.com/detail/Panchayat/0K7C58O4",
                "deep_link": "primevideo://detail?asin=B086887556"
            }
        ]
    },
    {
        "tmdb_id": "100088",
        "imdb_id": "tt8178634",
        "title": "Scam 1992: The Harshad Mehta Story",
        "type": "series",
        "runtime_minutes": 52,
        "release_year": 2020,
        "genres": "Biography, Crime, Drama",
        "mood_tags": "Adrenaline Rush, Intense Drama, Masterpiece, High-Stakes Action",
        "director": "Hansal Mehta, Jai Mehta",
        "cast_members": "Pratik Gandhi, Shreya Dhanwanthary, Hemant Kher, Anjali Barot",
        "rating_imdb": 9.3,
        "rating_tmdb": 8.7,
        "rating_rotten_tomatoes": 98,
        "overview": "Set in 1980's and 90's Bombay, Scam 1992 follows the life of stockbroker Harshad Mehta - who took the stock market to dizzying heights and his catastrophic downfall.",
        "poster_url": "https://image.tmdb.org/t/p/w500/y108eYp8n138v2K9A.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/y108eYp8n138v2K9A.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=ISORfez27og",
        "providers": [
            {
                "provider_id": "sonyliv",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.sonyliv.com/shows/scam-1992-the-harshad-mehta-story-1700000292",
                "deep_link": "sonyliv://content/show/1700000292"
            }
        ]
    },
    {
        "tmdb_id": "60574",
        "imdb_id": "tt2442560",
        "title": "Peaky Blinders",
        "type": "series",
        "runtime_minutes": 58,
        "release_year": 2013,
        "genres": "Crime, Drama",
        "mood_tags": "Dark & Gritty, Intense Drama, High-Stakes Action, Atmospheric",
        "director": "Steven Knight",
        "cast_members": "Cillian Murphy, Paul Anderson, Sophie Rundle, Helen McCrory, Tom Hardy",
        "rating_imdb": 8.8,
        "rating_tmdb": 8.5,
        "rating_rotten_tomatoes": 93,
        "overview": "A gangster family epic set in 1900s England, centering on a gang who sew razor blades in the peaks of their caps, and their fierce boss Tommy Shelby.",
        "poster_url": "https://image.tmdb.org/t/p/w500/vUUqzWa2LnHIVqkaKVlVGkVcZIW.jpg",
        "backdrop_url": "https://image.tmdb.org/t/p/w1280/wiE9NX0E6zgX958aJ6941u16w1.jpg",
        "trailer_url": "https://www.youtube.com/watch?v=oVzVdvGIC7U",
        "providers": [
            {
                "provider_id": "netflix",
                "access_type": "flatrate",
                "price": 0.0,
                "currency": "INR",
                "web_url": "https://www.netflix.com/title/80002479",
                "deep_link": "nflx://title/80002479"
            }
        ]
    }
]

PROVIDERS = PROVIDERS_DATA
TITLES = TITLES_DATA
INITIAL_SUBSCRIPTIONS = ["netflix", "prime_video", "hotstar"]

