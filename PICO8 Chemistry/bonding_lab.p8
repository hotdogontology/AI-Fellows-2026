pico-8 cartridge // http://www.pico-8.com
version 42
__lua__

-- bonding lab
-- left/right: change model
-- up/down: temperature
-- z: pause
-- x: reset

mode=1
temperature=1
paused=false

function _init()
 reset()
end

function reset()
 atoms={}
 bonds={}
 electrons={}
 transfers={}
 paused=false

 if mode==1 then
  init_covalent()
 elseif mode==2 then
  init_ionic()
 else
  init_metallic()
 end
end

function new_atom(x,y,kind,col,r)
 local a={
  x=x,y=y,
  vx=rnd(1)-0.5,
  vy=rnd(1)-0.5,
  kind=kind,
  col=col,
  r=r or 4,
  charge=0,
  cap=0,
  bonds=0
 }
 add(atoms,a)
 return a
end

function init_covalent()
 for i=1,10 do
  local a=new_atom(rnd(112)+8,rnd(92)+28,"h",7,4)
  a.cap=1
 end
end

function init_ionic()
 for i=1,5 do
  local a=new_atom(rnd(52)+8,rnd(92)+28,"na",9,5)
  a.cap=1
 end

 for i=1,5 do
  local a=new_atom(rnd(52)+68,rnd(92)+28,"cl",11,5)
  a.cap=1
 end
end

function init_metallic()
 for gy=0,3 do
  for gx=0,3 do
   local a=new_atom(rnd(104)+12,rnd(80)+36,"m",6,5)
   a.tx=38+gx*17
   a.ty=40+gy*17
   a.gx=gx
   a.gy=gy
   a.charge=1
  end
 end

 for i=1,24 do
  add(electrons,{
   x=rnd(72)+28,
   y=rnd(76)+34,
   vx=rnd(1)-0.5,
   vy=rnd(1)-0.5
  })
 end
end

function _update60()
 if btnp(0) then
  mode-=1
  if mode<1 then mode=3 end
  reset()
 end

 if btnp(1) then
  mode+=1
  if mode>3 then mode=1 end
  reset()
 end

 if btnp(2) then temperature=min(2,temperature+0.1) end
 if btnp(3) then temperature=max(0.1,temperature-0.1) end
 if btnp(4) then paused=not paused end
 if btnp(5) then reset() end

 if paused then return end

 if mode==1 then
  update_covalent()
 elseif mode==2 then
  update_ionic()
 else
  update_metallic()
 end

 update_transfers()
 keep_atoms_in_box()
end

function update_covalent()
 add_heat(0.018)

 for i=1,#atoms-1 do
  for j=i+1,#atoms do
   local a=atoms[i]
   local b=atoms[j]
   local dx=b.x-a.x
   local dy=b.y-a.y
   local d=max(0.01,sqrt(dx*dx+dy*dy))

   if not is_bonded(a,b) and
      a.bonds<a.cap and b.bonds<b.cap then
    if d<13 then
     add_bond(a,b,"covalent")
    elseif d<32 then
     pull(a,b,0.0015*(32-d))
    end
   end
  end
 end

 apply_bond_springs(11,0.015)
 repel_overlaps(0.025)
 damp_atoms(0.992)
end

function update_ionic()
 add_heat(0.015)

 for i=1,#atoms-1 do
  for j=i+1,#atoms do
   local a=atoms[i]
   local b=atoms[j]
   local dx=b.x-a.x
   local dy=b.y-a.y
   local d=max(0.01,sqrt(dx*dx+dy*dy))

   local mixed=(a.kind=="na" and b.kind=="cl") or
               (a.kind=="cl" and b.kind=="na")

   if mixed and a.charge==0 and b.charge==0 then
    if d<15 then
     local na=a
     local cl=b
     if a.kind=="cl" then
      na=b
      cl=a
     end

     na.charge=1
     cl.charge=-1
     add_bond(na,cl,"ionic")
     add(transfers,{a=na,b=cl,t=0})
    elseif d<38 then
     pull(a,b,0.0012*(38-d))
    end
   end

   if a.charge!=0 and b.charge!=0 and d<52 then
    local f=(-a.charge*b.charge)*0.018*(1-d/52)
    push_pair(a,b,f)
   end
  end
 end

 apply_bond_springs(13,0.018)
 repel_overlaps(0.03)
 damp_atoms(0.99)
end

function update_metallic()
 for a in all(atoms) do
  a.vx+=(a.tx-a.x)*0.003
  a.vy+=(a.ty-a.y)*0.003
  a.vx+=(rnd(1)-0.5)*temperature*0.008
  a.vy+=(rnd(1)-0.5)*temperature*0.008
 end

 repel_overlaps(0.02)
 damp_atoms(0.96)

 for e in all(electrons) do
  e.vx+=(rnd(1)-0.5)*0.08*temperature
  e.vy+=(rnd(1)-0.5)*0.08*temperature

  e.vx+=(64-e.x)*0.0004
  e.vy+=(74-e.y)*0.0004

  e.vx*=0.985
  e.vy*=0.985
  e.x+=e.vx
  e.y+=e.vy

  if e.x<24 then e.x=24 e.vx=abs(e.vx) end
  if e.x>104 then e.x=104 e.vx=-abs(e.vx) end
  if e.y<30 then e.y=30 e.vy=abs(e.vy) end
  if e.y>112 then e.y=112 e.vy=-abs(e.vy) end
 end
end

function add_heat(amount)
 for a in all(atoms) do
  a.vx+=(rnd(1)-0.5)*temperature*amount
  a.vy+=(rnd(1)-0.5)*temperature*amount
 end
end

function damp_atoms(amount)
 for a in all(atoms) do
  a.vx*=amount
  a.vy*=amount
 end
end

function keep_atoms_in_box()
 for a in all(atoms) do
  a.x+=a.vx
  a.y+=a.vy

  if a.x<a.r+3 then
   a.x=a.r+3
   a.vx=abs(a.vx)
  end

  if a.x>124-a.r then
   a.x=124-a.r
   a.vx=-abs(a.vx)
  end

  if a.y<a.r+25 then
   a.y=a.r+25
   a.vy=abs(a.vy)
  end

  if a.y>124-a.r then
   a.y=124-a.r
   a.vy=-abs(a.vy)
  end
 end
end

function repel_overlaps(strength)
 for i=1,#atoms-1 do
  for j=i+1,#atoms do
   local a=atoms[i]
   local b=atoms[j]
   local dx=b.x-a.x
   local dy=b.y-a.y
   local d=max(0.01,sqrt(dx*dx+dy*dy))
   local gap=a.r+b.r+2

   if d<gap then
    push_pair(a,b,-strength*(gap-d))
   end
  end
 end
end

function push_pair(a,b,f)
 local dx=b.x-a.x
 local dy=b.y-a.y
 local d=max(0.01,sqrt(dx*dx+dy*dy))
 local nx=dx/d
 local ny=dy/d

 a.vx+=nx*f
 a.vy+=ny*f
 b.vx-=nx*f
 b.vy-=ny*f
end

function pull(a,b,f)
 push_pair(a,b,f)
end

function add_bond(a,b,kind)
 if is_bonded(a,b) then return end
 add(bonds,{a=a,b=b,kind=kind})
 a.bonds+=1
 b.bonds+=1
end

function is_bonded(a,b)
 for bond in all(bonds) do
  if (bond.a==a and bond.b==b) or
     (bond.a==b and bond.b==a) then
   return true
  end
 end
 return false
end

function apply_bond_springs(rest,k)
 for bond in all(bonds) do
  local a=bond.a
  local b=bond.b
  local dx=b.x-a.x
  local dy=b.y-a.y
  local d=max(0.01,sqrt(dx*dx+dy*dy))
  push_pair(a,b,k*(d-rest))
 end
end

function update_transfers()
 for i=#transfers,1,-1 do
  local t=transfers[i]
  t.t+=0.035
  if t.t>1 then
   deli(transfers,i)
  end
 end
end

function _draw()
 cls(1)
 rectfill(0,0,127,22,0)

 if mode==1 then
  draw_covalent()
 elseif mode==2 then
  draw_ionic()
 else
  draw_metallic()
 end

 draw_atoms()
 draw_transfers()
 draw_ui()
end

function draw_covalent()
 for bond in all(bonds) do
  local a=bond.a
  local b=bond.b
  line(a.x,a.y,b.x,b.y,6)

  local mx=(a.x+b.x)/2
  local my=(a.y+b.y)/2
  local dx=b.x-a.x
  local dy=b.y-a.y
  local d=max(0.01,sqrt(dx*dx+dy*dy))
  local px=-dy/d
  local py=dx/d

  circfill(mx+px*2,my+py*2,1,10)
  circfill(mx-px*2,my-py*2,1,10)
 end
end

function draw_ionic()
 for bond in all(bonds) do
  local a=bond.a
  local b=bond.b
  local dx=b.x-a.x
  local dy=b.y-a.y

  for s=0.15,0.85,0.2 do
   pset(a.x+dx*s,a.y+dy*s,13)
  end
 end
end

function draw_metallic()
 for a in all(atoms) do
  for b in all(atoms) do
   local grid_neighbor=
    (a.gx+1==b.gx and a.gy==b.gy) or
    (a.gy+1==b.gy and a.gx==b.gx)

   if grid_neighbor then
    local dx=b.x-a.x
    local dy=b.y-a.y
    local d=sqrt(dx*dx+dy*dy)
    if d<24 then
     line(a.x,a.y,b.x,b.y,5)
    end
   end
  end
 end

 for e in all(electrons) do
  circfill(e.x,e.y,1,10)
 end
end

function draw_atoms()
 for a in all(atoms) do
  circfill(a.x,a.y,a.r,a.col)
  circ(a.x,a.y,a.r,7)

  if a.kind=="h" then
   print("h",a.x-2,a.y-2,0)
  elseif a.kind=="na" then
   print("na",a.x-4,a.y-2,0)
  elseif a.kind=="cl" then
   print("cl",a.x-4,a.y-2,0)
  else
   print("m",a.x-2,a.y-2,0)
  end

  if a.charge==1 then
   print("+",a.x+3,a.y-7,7)
  elseif a.charge==-1 then
   print("-",a.x+3,a.y-7,7)
  end
 end
end

function draw_transfers()
 for t in all(transfers) do
  local x=t.a.x+(t.b.x-t.a.x)*t.t
  local y=t.a.y+(t.b.y-t.a.y)*t.t
  circfill(x,y,1,10)
 end
end

function draw_ui()
 local names={"covalent","ionic","metallic"}
 local bonded=flr(#bonds)

 print(names[mode].." bonding",3,2,7)

 if mode==1 then
  print("shared electron pairs: "..bonded,3,9,6)
 elseif mode==2 then
  print("electrons transferred: "..bonded,3,9,13)
 else
  print("mobile electrons: "..#electrons,3,9,10)
 end

 print("temp:"..flr(temperature*10)/10,96,2,7)

 if paused then
  print("paused",50,17,8)
 else
  print("left/right mode  z pause  x reset",3,17,5)
 end

 if mode==1 then
  print("nonmetals share electrons",17,121,7)
 elseif mode==2 then
  print("opposite ions attract",22,121,7)
 else
  print("ions + a shared electron sea",10,121,7)
 end
end
