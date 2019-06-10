 /*
 * Magazine sample
 */

function addPagei(page, book,i) {
    
    var id, pages = book.turn('pages');
    
    // Create a new element for this page
    var element = $('<div />', {});
    
    // Add the page to the flipbook
    if (book.turn('addPage', element, page)) {
        
        // Add the initial HTML
        // It will contain a loader indicator and a gradient
        element.html('<div class="gradient"></div><div class="loader"></div>');
        
        // Load the page
        loadPagei(page, element,i);
    }
    
}

function loadPagei(page, pageElement,i) {
    
    // Create an image element
    
    var img = $('<img />');
    
    img.mousedown(function(e) {
                  e.preventDefault();
                  });
    
    img.load(function() {
             
             // Set the size
             $(this).css({width: '100%', height: '100%'});
             
             // Add the image to the page after loaded
             
             $(this).appendTo(pageElement);
             
             // Remove the loader indicator
             
             pageElement.find('.loader').remove();
             });
    
    // Load the page
    
    img.attr('src', 'pages/'+i+'/regular/'+  page );
    
    
}


// Load small page

function loadSmallPagei(page, pageElement,i) {
    
    var img = pageElement.find('img');
    
    img.css({width: '100%', height: '100%'});
    
    img.unbind('load');
    // Loadnew page
    
    img.attr('src', 'pages/'+i+'/regular/' +  page);
}

// http://code.google.com/p/chromium/issues/detail?id=128488

function isChrome() {
    
    return navigator.userAgent.indexOf('Chrome')!=-1;
    
}

function disableControls(page) {

    
}

// Set the width and height for the viewport

function resizeViewporti(i) {
    
    var width = ($('#book_'+i+'_container').width()-$('.previous-button'+i).width()-$('.previous-button'+i).width()),
    height = ($('#book_'+i+'_container').width()-$('.previous-button'+i).width()-$('.previous-button'+i).width()),
    options = $('#book'+i).turn('options');
    $('#book'+i).removeClass('animated');

   
    
    $('.magazine-viewport').css({width: width,
                                height: height});
        
        if (width!=$('#book'+i).width() || height!=$('#book'+i).height()) {

            if ($('#book'+i).turn('page')==1)
                $('#book'+i).turn('peel', 'br');
            
            $('.next-button'+i).css({height: height, backgroundPosition: '-38px '+(height/2-32/2)+'px',width:12});
            $('.previous-button'+i).css({height:height, backgroundPosition: '-4px '+(height/2-32/2)+'px',width:12});
            $('#book'+i).turn('size', width, height);

        }
        
            $('#book'+i).css({top: 5, right: $('.previous-button').width()+10})

    var magazineOffset = $('#book'+i).offset();

    

    if (magazineOffset.top<$('.made').height())
        $('.made').hide();
    else
        $('.made').show();
    
    $('#book'+i).addClass('animated');
    
}


// Number of views in a flipbook

function numberOfViews(book) {
    return book.turn('pages') / 2 + 1;
}

// Current view in a flipbook

function getViewNumber(book, page) {
    return parseInt((page || book.turn('page'))/2 + 1, 10);
}

function moveBar(yes) {
    if (Modernizr && Modernizr.csstransforms) {
        $('#slider .ui-slider-handle').css({zIndex: yes ? -1 : 10000});
    }
}

function setPreview(view) {
   
}

// Width of the flipbook when esced in

function largeMagazineWidthi(i) {
    
    return  $('#book_'+i+'_container').width();
    
}

// decode URL Parameters

function decodeParams(data) {
    
    var parts = data.split('&'), d, obj = {};
    
    for (var i =0; i<parts.length; i++) {
        d = parts[i].split('=');
        obj[decodeURIComponent(d[0])] = decodeURIComponent(d[1]);
    }
    
    return obj;
}

// Calculate the width and height of a square within another square

function calculateBound(d) {
    
    var bound = {width: d.width, height: d.height};
    
    if (bound.width>d.boundWidth || bound.height>d.boundHeight) {
        
        var rel = bound.width/bound.height;
        
        if (d.boundWidth/rel>d.boundHeight && d.boundHeight*rel<=d.boundWidth) {
            
            bound.width = Math.round(d.boundHeight*rel);
            bound.height = d.boundHeight;
            
        } else {
            
            bound.width = d.boundWidth;
            bound.height = Math.round(d.boundWidth/rel);
            
        }
    }
    
    return bound;
}

function loadApp3() {
    
    $('#canvas3').fadeIn(2000);
    
    var flipbook = $('#book3');
    
    // Check if the CSS was already loaded
    
    if (flipbook.width()==0 || flipbook.height()==0) {
        setTimeout(loadApp3, 10);
        return;
    }
    
    // Create the flipbook
    
    flipbook.turn({
                  
                  // Magazine width
                  
                  width:  $('#book_3_container').width(),
                  
                  // Magazine height
                  
                  height:  $('#book_3_container').width()*0.75,
                  
                  // Duration in millisecond
                  
                  duration: 1000,
                  
                  // Hardware acceleration
                  
                  acceleration: !isChrome(),
                  
                  // Enables gradients
                  
                  gradients: true,
                  
                  // Auto center this flipbook
                  
                  autoCenter: true,
                  
                  // Elevation from the edge of the flipbook when turning a page
                  
                  elevation: 50,
                  
                  // The number of pages
                  
                  pages: 5,
                  
                  // Events
                  
                  when: {
                  turning: function(event, page, view) {
                  
                  var book = $(this),
                  currentPage = book.turn('page'),
                  pages = book.turn('pages');
                  
                  // Update the current URI
                  
                  Hash.go('page/' + page).update();
                  
                  // Show and hide navigation buttons
                  
                  disableControls(page);
                  
                  
                  $('.thumbnails2 .page-'+currentPage).
                  parent().
                  removeClass('current');
                  
                  $('.thumbnails2 .page-'+page).
                  parent().
                  addClass('current');
                  
                  
                  
                  },
                  
                  turned: function(event, page, view) {
                  
                  disableControls(page);
                  
                  $(this).turn('center');
                  
                  if (page==1) {
                  $(this).turn('peel', 'br');
                  }
                  
                  },
                  
                  missing: function (event, pages) {
                  
                  // Add pages that aren't in the magazine
                  
                  for (var i = 1; i < pages.length; i++)
                  addPagei(pages[i], $(this),3);
                  
                  }
                  }
                  
                  });
    
    
    // Using arrow keys to turn the page
    
    $(document).keydown(function(e){
                        
                        var previous = 37, next = 39;
                        
                        switch (e.keyCode) {
                        case previous:
                        
                        // left arrow
                        $('#book3').turn('previous');
                        e.preventDefault();
                        
                        break;
                        case next:
                        
                        //right arrow
                        $('#book3').turn('next');
                        e.preventDefault();
                        
                        break;
                        
                        }
                        });
    
    // URIs - Format #/page/1
    
    Hash.on('^page\/([0-9]*)$', {
            yep: function(path, parts) {
            var page = parts[1];
            
            if (page!==undefined) {
            if ($('#book3').turn('is'))
            $('#book3').turn('page', page);
            }
            
            },
            nop: function(path) {
            
            if ($('#book3').turn('is'))
            $('#book3').turn('page', 1);
            }
            });
    
    

    
    // Events for thumbnails
    
    
    
    // Events for the next button
    
    $('.next-button3').bind($.mouseEvents.over, function() {
                            
                            $(this).addClass('next-button-hover');
                            
                            }).bind($.mouseEvents.out, function() {
                                    
                                    $(this).removeClass('next-button-hover');
                                    
                                    }).bind($.mouseEvents.down, function() {
                                            
                                            $(this).addClass('next-button-down');
                                            
                                            }).bind($.mouseEvents.up, function() {
                                                    
                                                    $(this).removeClass('next-button-down');
                                                    
                                                    }).click(function() {
                                                             
                                                             $('#book3').turn('next');
                                                             
                                                             });
    
    // Events for the next button
    
    $('.previous-button3').bind($.mouseEvents.over, function() {
                                
                                $(this).addClass('previous-button-hover');
                                
                                }).bind($.mouseEvents.out, function() {
                                        
                                        $(this).removeClass('previous-button-hover');
                                        
                                        }).bind($.mouseEvents.down, function() {
                                                
                                                $(this).addClass('previous-button-down');
                                                
                                                }).bind($.mouseEvents.up, function() {
                                                        
                                                        $(this).removeClass('previous-button-down');
                                                        
                                                        }).click(function() {
                                                                 
                                                                 $('#book3').turn('previous');
                                                                 
                                                                 });
    
    
    resizeViewporti(3);
    
    $('#book3').addClass('animated');
    
    }
function loadApp4() {
    
    $('#canvas4').fadeIn(1000);
    
    var flipbook = $('#book4');
    
    // Check if the CSS was already loaded
    
    if (flipbook.width()==0 || flipbook.height()==0) {
        setTimeout(loadApp, 10);
        return;
    }
    
    // Create the flipbook
    
    flipbook.turn({
                  
                  // Magazine width
                  
                  width: $('#book_4_container').width(),
                  
                  // Magazine height
                  
                  height:  $('#book_4_container').width()*0.75,
                  
                  // Duration in millisecond
                  
                  duration: 1000,
                  
                  // Hardware acceleration
                  
                  acceleration: !isChrome(),
                  
                  // Enables gradients
                  
                  gradients: true,
                  
                  // Auto center this flipbook
                  
                  autoCenter: true,
                  
                  // Elevation from the edge of the flipbook when turning a page
                  
                  elevation: 50,
                  
                  // The number of pages
                  
                  pages: 5,
                  
                  // Events
                  
                  when: {
                  turning: function(event, page, view) {
                  
                  var book = $(this),
                  currentPage = book.turn('page'),
                  pages = book.turn('pages');
                  
                  // Update the current URI
                  
                  Hash.go('page/' + page).update();
                  
                  // Show and hide navigation buttons
                  
                  disableControls(page);
                  
                  
                  $('.thumbnails3 .page-'+currentPage).
                  parent().
                  removeClass('current');
                  
                  $('.thumbnails3 .page-'+page).
                  parent().
                  addClass('current');
                  
                  
                  
                  },
                  
                  turned: function(event, page, view) {
                  
                  disableControls(page);
                  
                  $(this).turn('center');
                  
                  if (page==1) {
                  $(this).turn('peel', 'br');
                  }
                  
                  },
                  
                  missing: function (event, pages) {
                  
                  // Add pages that aren't in the magazine
                  
                  for (var i = 1; i < pages.length; i++)
                  addPagei(pages[i], $(this),4);
                  
                  }
                  }
                  
                  });
    
    // Zoom.js
    
    
    
    // Using arrow keys to turn the page
    
    $(document).keydown(function(e){
                        
                        var previous = 37, next = 39;
                        
                        switch (e.keyCode) {
                        case previous:
                        
                        // left arrow
                        $('#book4').turn('previous');
                        e.preventDefault();
                        
                        break;
                        case next:
                        
                        //right arrow
                        $('#book4').turn('next');
                        e.preventDefault();
                        
                        break;
                        
                        }
                        });
    
    // URIs - Format #/page/1
    
    Hash.on('^page\/([0-9]*)$', {
            yep: function(path, parts) {
            var page = parts[1];
            
            if (page!==undefined) {
            if ($('.magazine').turn('is'))
            $('.magazine').turn('page', page);
            }
            
            },
            nop: function(path) {
            
            if ($('.magazine').turn('is'))
            $('.magazine').turn('page', 1);
            }
            });
    
    
    $(window).resize(function() {
                     resizeViewporti(4);
                     }).bind('orientationchange', function() {
                             resizeViewporti(4);
                             });
    
    // Events for the next button
    
    $('.next-button4').bind($.mouseEvents.over, function() {
                            
                            $(this).addClass('next-button-hover');
                            
                            }).bind($.mouseEvents.out, function() {
                                    
                                    $(this).removeClass('next-button-hover');
                                    
                                    }).bind($.mouseEvents.down, function() {
                                            
                                            $(this).addClass('next-button-down');
                                            
                                            }).bind($.mouseEvents.up, function() {
                                                    
                                                    $(this).removeClass('next-button-down');
                                                    
                                                    }).click(function() {
                                                             
                                                             $('#book4').turn('next');
                                                             
                                                             });
    
    // Events for the next button
    
    $('.previous-button4').bind($.mouseEvents.over, function() {
                                
                                $(this).addClass('previous-button-hover');
                                
                                }).bind($.mouseEvents.out, function() {
                                        
                                        $(this).removeClass('previous-button-hover');
                                        
                                        }).bind($.mouseEvents.down, function() {
                                                
                                                $(this).addClass('previous-button-down');
                                                
                                                }).bind($.mouseEvents.up, function() {
                                                        
                                                        $(this).removeClass('previous-button-down');
                                                        
                                                        }).click(function() {
                                                                 
                                                                 $('#book4').turn('previous');
                                                                 
                                                                 });
    
    
    resizeViewporti(4);
    
    $('#book4').addClass('animated');
    
}
function loadApp2() {
    
    $('#canvas2').fadeIn(1000);
    
    var flipbook = $('#book2');
    
    // Check if the CSS was already loaded
    
    if (flipbook.width()==0 || flipbook.height()==0) {
        setTimeout(loadApp, 10);
        return;
    }
    
    // Create the flipbook
    
    flipbook.turn({
                  
                  // Magazine width
                  
                  width:  $('#book_2_container').width(),
                  
                  // Magazine height
                  
                  height:  $('#book_2_container').width()*0.75,
                  
                  // Duration in millisecond
                  
                  duration: 1000,
                  
                  // Hardware acceleration
                  
                  acceleration: !isChrome(),
                  
                  // Enables gradients
                  
                  gradients: true,
                  
                  // Auto center this flipbook
                  
                  autoCenter: true,
                  
                  // Elevation from the edge of the flipbook when turning a page
                  
                  elevation: 50,
                  
                  // The number of pages
                  
                  pages: 5,
                  
                  // Events
                  
                  when: {
                  turning: function(event, page, view) {
                  
                  var book = $(this),
                  currentPage = book.turn('page'),
                  pages = book.turn('pages');
                  
                  // Update the current URI
                  
                  Hash.go('page/' + page).update();
                  
                  // Show and hide navigation buttons
                  
                  disableControls(page);
                  
                  
                  $('.thumbnails1 .page-'+currentPage).
                  parent().
                  removeClass('current');
                  
                  $('.thumbnails1 .page-'+page).
                  parent().
                  addClass('current');
                  
                  
                  
                  },
                  
                  turned: function(event, page, view) {
                  
                  disableControls(page);
                  
                  $(this).turn('center');
                  
                  if (page==1) {
                  $(this).turn('peel', 'br');
                  }
                  
                  },
                  
                  missing: function (event, pages) {
                  
                  // Add pages that aren't in the magazine
                  
                  for (var i = 1; i < pages.length; i++)
                  addPagei(pages[i], $(this),2);
                  
                  }
                  }
                  
                  });
    
    
    // Using arrow keys to turn the page
    
    $(document).keydown(function(e){
                        
                        var previous = 37, next = 39;
                        
                        switch (e.keyCode) {
                        case previous:
                        
                        // left arrow
                        $('#book2').turn('previous');
                        e.preventDefault();
                        
                        break;
                        case next:
                        
                        //right arrow
                        $('#book2').turn('next');
                        e.preventDefault();
                        
                        break;
                        
                        }
                        });
    
    // URIs - Format #/page/1
    
    Hash.on('^page\/([0-9]*)$', {
            yep: function(path, parts) {
            var page = parts[1];
            
            if (page!==undefined) {
            if ($('.magazine').turn('is'))
            $('.magazine').turn('page', page);
            }
            
            },
            nop: function(path) {
            
            if ($('.magazine').turn('is'))
            $('.magazine').turn('page', 1);
            }
            });
    
    
    $(window).resize(function() {
                     resizeViewporti(2);
                     }).bind('orientationchange', function() {
                             resizeViewporti(2);
                             });
    
    
    // Events for the next button
    
    $('.next-button2').bind($.mouseEvents.over, function() {
                            
                            $(this).addClass('next-button-hover');
                            
                            }).bind($.mouseEvents.out, function() {
                                    
                                    $(this).removeClass('next-button-hover');
                                    
                                    }).bind($.mouseEvents.down, function() {
                                            
                                            $(this).addClass('next-button-down');
                                            
                                            }).bind($.mouseEvents.up, function() {
                                                    
                                                    $(this).removeClass('next-button-down');
                                                    
                                                    }).click(function() {
                                                             
                                                             $('#book2').turn('next');
                                                             
                                                             });
    
    // Events for the next button
    
    $('.previous-button2').bind($.mouseEvents.over, function() {
                                
                                $(this).addClass('previous-button-hover');
                                
                                }).bind($.mouseEvents.out, function() {
                                        
                                        $(this).removeClass('previous-button-hover');
                                        
                                        }).bind($.mouseEvents.down, function() {
                                                
                                                $(this).addClass('previous-button-down');
                                                
                                                }).bind($.mouseEvents.up, function() {
                                                        
                                                        $(this).removeClass('previous-button-down');
                                                        
                                                        }).click(function() {
                                                                 
                                                                 $('#book2').turn('previous');
                                                                 
                                                                 });
    
    
    resizeViewporti(2);
    
    $('#book2').addClass('animated');
    
    }
function loadApp1() {
    
    $('#canvas1').fadeIn(1000);
    
    var flipbook = $('#book1');
    
    // Check if the CSS was already loaded
    
    if (flipbook.width()==0 || flipbook.height()==0) {
        setTimeout(loadApp, 10);
        return;
    }
    
    // Create the flipbook
    
    flipbook.turn({
                  
                  // Magazine width
                  
                  width: $('#book_1_container').width(),
                  
                  // Magazine height
                  
                  height:  $('#book_1_container').width()*0.75,
                  
                  // Duration in millisecond
                  
                  duration: 1000,
                  
                  // Hardware acceleration
                  
                  acceleration: !isChrome(),
                  
                  // Enables gradients
                  
                  gradients: true,
                  
                  // Auto center this flipbook
                  
                  autoCenter: true,
                  
                  // Elevation from the edge of the flipbook when turning a page
                  
                  elevation: 50,
                  
                  // The number of pages
                  
                  pages: 5,
                  
                  // Events
                  
                  when: {
                  turning: function(event, page, view) {
                  
                  var book = $(this),
                  currentPage = book.turn('page'),
                  pages = book.turn('pages');
                  
                  // Update the current URI
                  
                  Hash.go('page/' + page).update();
                  
                  // Show and hide navigation buttons
                  
                  disableControls(page);
                  
                  
                  $('.thumbnails .page-'+currentPage).
                  parent().
                  removeClass('current');
                  
                  $('.thumbnails .page-'+page).
                  parent().
                  addClass('current');
                  
                  
                  
                  },
                  
                  turned: function(event, page, view) {
                  
                  disableControls(page);
                  
                  $(this).turn('center');
                  
                  if (page==1) {
                  $(this).turn('peel', 'br');
                  }
                  
                  },
                  
                  missing: function (event, pages) {
                  
                  // Add pages that aren't in the magazine
                  
                  for (var i = 1; i < pages.length; i++)
                  addPagei(pages[i], $(this),1);
                  
                  }
                  }
                  
                  });
    
    // Zoom.js
    
    
    // Using arrow keys to turn the page
    
    $(document).keydown(function(e){
                        
                        var previous = 37, next = 39;
                        
                        switch (e.keyCode) {
                        case previous:
                        
                        // left arrow
                        $('#book1').turn('previous');
                        e.preventDefault();
                        
                        break;
                        case next:
                        
                        //right arrow
                        $('#book1').turn('next');
                        e.preventDefault();
                        
                        break;
                        
                        }
                        });
    
    // URIs - Format #/page/1
    
    Hash.on('^page\/([0-9]*)$', {
            yep: function(path, parts) {
            var page = parts[2];
            
            if (page!==undefined) {
            if ($('.magazine').turn('is'))
            $('.magazine').turn('page', page);
            }
            
            },
            nop: function(path) {
            
            if ($('.magazine').turn('is'))
            $('.magazine').turn('page', 1);
            }
            });
    
    
    
    
    // Events for the next button
    
    $('.next-button1').bind($.mouseEvents.over, function() {
                           
                           $(this).addClass('next-button-hover');
                           
                           }).bind($.mouseEvents.out, function() {
                                   
                                   $(this).removeClass('next-button-hover');
                                   
                                   }).bind($.mouseEvents.down, function() {
                                           
                                           $(this).addClass('next-button-down');
                                           
                                           }).bind($.mouseEvents.up, function() {
                                                   
                                                   $(this).removeClass('next-button-down');
                                                   
                                                   }).click(function() {
                                                            
                                                            $('#book1').turn('next');
                                                            
                                                            });
    
    // Events for the next button
    
    $('.previous-button1').bind($.mouseEvents.over, function() {
                               
                               $(this).addClass('previous-button-hover');
                               
                               }).bind($.mouseEvents.out, function() {
                                       
                                       $(this).removeClass('previous-button-hover');
                                       
                                       }).bind($.mouseEvents.down, function() {
                                               
                                               $(this).addClass('previous-button-down');
                                               
                                               }).bind($.mouseEvents.up, function() {
                                                       
                                                       $(this).removeClass('previous-button-down');
                                                       
                                                       }).click(function() {
                                                                
                                                                $('#book1').turn('previous');
                                                                
                                                                });
    
    resizeViewporti(1);
    
    
    $('#book1').addClass('animated');
    
}
