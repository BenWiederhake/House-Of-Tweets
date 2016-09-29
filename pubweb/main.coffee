#= require <birds_de_dyn.coffee>
#= require <birds_en_dyn.coffee>

require('../ext/node_modules/jquery-on-infinite-scroll')

###
	<!-- &url=https%3A%2F%2FHouseOfTweets.github.io -->

		<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3 text-center">
			<a href="https://twitter.com/intent/tweet?text=#{name}&button_hashtag=HouseOfTweets">
				<img src="imgs/#{bid}.jpg" alt="#{name}" width="200" height="150">
				<span>#{name} #HouseOfTweets</span>
			</a>
		</div>
###

placeBird = (name, bid) ->
	console.log "Loadin' moar"
	# Although I call it "_tag", it's always a jQuery wrapped tag, not a "raw" tag.
	#img_tag = $("<img src=\"imgs/#{bid}\" alt=\"#{name}\" width=\"200\" height=\"150\">")
	img_tag = $("<img src=\"imgs/flag_de.png?#{bid}\" alt=\"#{name}\" width=\"200\" height=\"150\">")
	span_tag = $("<span>")
	# TODO: Why can't I just write the text in the jQuery call?
	span_tag.text("#{name} #HouseOfTweets")
	a_tag = $("<a>")
	name_for_href = encodeURIComponent(name)
	a_tag.attr("href", "https://twitter.com/intent/tweet?text=#{name_for_href}&button_hashtag=HouseOfTweets")
	a_tag.append(img_tag)
	a_tag.append(span_tag)
	div_tag = $('<div class="col-xs-12 col-sm-6 col-md-4 col-lg-3 text-center">')
	div_tag.append(a_tag)
	$("#hot-birdslist").append(div_tag)

placePseudoBird = ->
	placeBird("Weißkopfseeländer", "argh")

# A single cell is ${image height} + 52 pixels high
# (unless there's word wrap, but we'll assume there isn't)
$.onInfiniteScroll(placePseudoBird, { offset: 202 + 20 })
