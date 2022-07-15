# Future development tasks

## Minor isssues to fix
 - Don't allow save button to overwrite non-image files (based on file extension)

## Minor features
 - Add missing params to UI:
  * ddim/ddpm
 - Display client/server errors in the UI
 - Show window immediately in inpainting_ui, show loading indicator while models load
 - Sample selection improvements:
  * Add "zoom" option to inspect samples more closely
 - Add undo/redo buttons to mask area
 - Add undo/redo buttons to main image
 - Add "new image" option with custom resolution

## More ambitious features:
 - Clip ranking within the UI:
  * Show as numbers, bars of relative length, under image samples
 - Create optional inpainting timelapse animations
  * Save image every time after changes applied, use images as video frames
  * Use command line to enable, providing optional starting video for continuing sessions
 - Update server to allow for multiple clients:
  * Tie inpainting requests to UUID, require UUID to get results
  * Queue requests, reject if queue exceeds some length
  * Use DELETE to cancel queued requests
  * Remove results after a delay, use longer delay if images aren't fetched.
 - Add basic drawing tools to help suggest content to inpainting engine.
  * Add a "sketch" layer to mask creator
    * Toggle between sketch and mask drawing
    * Hide mask when in sketch mode
    * Add color picker, eyedropper for sketch mode
    * Track sketch mode brush size separately
  * Apply sketch layer as overlay to edited area before inpainting

## Interesting ideas I probably won't pursue:
 - Add upscaling controls using RealESRGAN or similar as backend.
 - Alternate image generation backends: are better systems available?
 - Alternate image editing frontends:
  * Browser-based frontend
  * Plugins for GIMP or other editors
  * Mobile application
 - Clean up autoedit.py, add it as an option to the UI
