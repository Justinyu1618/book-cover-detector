# Book Cover Detector

![gif](https://github.com/Justinyu1618/book-cover-detector/blob/master/dis_cover.gif?raw=true)

## Development
Change secrets.txt --> secrets.py and populate with secrets


## API Spec
There's only one endpoint

### Request
**URL** : `https://coverscan.herokuapp.com/get_data`

**Methods**
* GET: (for testing purposes only)
	* `image=sample_covers/[ name of cover image ]`
* POST:
	* body:
 ```{ image: "base64 encoding of image"}```

**Other Parameters**

`data_type=` 
* `primary` - response returns primary data
* `secondary` - response returns secondary data
* blank - response returns both

`isbn=`
* isbn number of book
* **required** if `data_type=secondary`


### Response
**Body:**
```
{
	"success": , //True if any data is returned
	"image_link": , // link to book cover
	"primary_data": {
		"amazon": , //amazon product link
		"title": , //book title
		"text_reviews_count": , //# of reviews on GoodReads
		"average_rating": , //GoodReads rating
		"description": , //book summary
		"isbn": , //isbn number
		"authors": { 
			"author": {
				"name": , //name of author
				"average_rating": , //author rating on goodreads
				"id": , //goodreads id
				"image_url": {
					"#text": , //link
					"@nophoto": , //whether there isn't a photo? lol
				},
				"small_image_url": {
					// ... same as "image_url" ...
				},
				"ratings_count": , //number of ratings
				"role": , // ?
				"link": , //goodreads profile
			}
		},
		"num_pages": ,
		"ratings_count": ,//# of goodreads ratings
		"similar_books": {
			// ... don't worry about this lol ... 
		},
	},
	"secondary_data": {
		"price": , //amazon price
		"reviews": [
			{ 
				"date": , //date of review
				"description": , //review body
				"name": , //reviewer name
				"profile_img": , //link to image
				"rating": , //out of 5.0
				"title": , //review_title
			},
			// ...
		]
	}
}
```

### Example API Calls:

Get request for all data
`https://coverscan.herokuapp.com/get_data/image=sample_covers/acceptance.jpg`

POST request for all data
`https://coverscan.herokuapp.com/get_data/`
body: `{ "image": "base64 image"}`

POST request for primary data
`https://coverscan.herokuapp.com/get_data/data_type=primary`
body: `{ "image": "base64 image"}`

POST request for secondary data
`https://coverscan.herokuapp.com/get_data/data_type=secondary&isbn=0374104115`
body: `{ "image": "base64 image"}`
