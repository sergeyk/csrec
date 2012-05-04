import Image, ImageDraw

def plot_host(sq, reqs, cluster):
  # ========= PLOT THIS HOST ================
  x_off = 20
  y_off = 20
  width = 1040
  height = 680
  w = width - x_off
  h = height - y_off
  
  im = Image.new("RGB",(width, height), 'white')
  draw = ImageDraw.Draw(im)

  draw.line((x_off, y_off) + (x_off, height), fill=128)
  draw.line((x_off, y_off) + (width, y_off), fill=128)
  
  max_dep = sq.get_max_depart(reqs)
  min_arr = sq.get_min_arrive(reqs)  
  delta_period = (max_dep - min_arr).total_seconds()
  
  min_req = sq.get_min_request(reqs)
  max_req = sq.get_max_request(reqs)
  delta_req = (max_req - min_req).total_seconds()

  red_rects = []
  red_lines = []
  rsp_duration = []
  
  last_cluster = -1
  
  start_point = (sq.convert_datetime(reqs[0]['rmd']) - min_req).total_seconds()-60
  
  colors = [(0,1,0), (1,0,0), (0,0,1)]

  for rq_idx, req in enumerate(reqs):
    arrival = (sq.convert_datetime(req['date_arrival']) - min_arr).total_seconds()/delta_period
    depart = (sq.convert_datetime(req['date_departure']) - min_arr).total_seconds()/delta_period
    req_time = (sq.convert_datetime(req['rcd']) - min_req).total_seconds()
    rsp_time_x = (sq.convert_datetime(req['rmd']) - min_arr).total_seconds()
    rsp_time_y = (sq.convert_datetime(req['rmd']) - min_req).total_seconds()
    rsp_duration.append(rsp_time_y - req_time)
    rect = [x_off + w* arrival, y_off + req_time/delta_req*h-5, x_off + w*depart, y_off + req_time/delta_req*h+5]
    rect2 = [x_off-5, y_off + rsp_time_y/delta_req*h-1, x_off+5, y_off + rsp_time_y/delta_req*h+1]
    rect3 = [y_off + rsp_time_x/delta_period*w-1,x_off-5, y_off + rsp_time_x/delta_period*w+1,  x_off+5]
    
    accepted = req['status']
    if accepted == 'Y':
      red_rects.append(rect)
      red_rects.append(rect2)
      red_rects.append(rect3)
      red_lines.append(((rect2[2], rect2[1]+1), (rect[0],rect[1]+3)))
      #red_lines.append(((rect3[2]-1, rect3[1]+1), (rect[0],rect[1]+3)))
    
    else:
      draw.rectangle(rect, fill='#B1B1B1', outline='black')
      draw.rectangle(rect2, fill='#B1B1B1', outline='black')
      draw.rectangle(rect3, fill='#B1B1B1', outline='black')
      color = colors[cluster[rq_idx]%3]
      draw.line((rect2[2], rect2[1]+1) + (rect[0],rect[1]+3), fill=color)
      #draw.line((rect3[2], rect3[1]+1) + (rect[0],rect[1]+3), fill=256)
    
    cluster_ind = cluster[rq_idx]
    if not cluster_ind == last_cluster:
      # we found a new cluster. draw a vertical line from last point to here.
      end_point = rsp_time_y + 60
      draw.line((x_off/2,y_off + start_point/delta_req*h)+(x_off/2,y_off + end_point/delta_req*h), fill=256)
       
      last_cluster = cluster_ind      
      if rq_idx+1< len(reqs):
        start_point = (sq.convert_datetime(reqs[rq_idx+1]['rmd']) - min_req).total_seconds()-60    
      
  #print len(red_rects)  
  for rect in red_rects:
    draw.rectangle(rect, fill='#FF0000', outline='black')

  for line in red_lines:
    draw.line(line[0] + line[1], fill=255)
      
  im.show()
  #im.save('late_response_guy.png')
  del im
  del draw 
