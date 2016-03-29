var Game = {};

Game.fps = 30;
Game.track_pos = new Vector(100, 0);
Game.track_area = new Vector(800, 700);

Game.highscores = [{name: '----------', points: 0}, {name: '----------', points: 0}, 
        {name: '----------', points: 0}, {name: '----------', points: 0}, 
        {name: '----------', points: 0}, {name: '----------', points: 0},  
        {name: '----------', points: 0}, {name: '----------', points: 0}, 
        {name: '----------', points: 0}, {name: '----------', points: 0}]

Game.getIDfor = function(ent) {
    this.entCount++;
    return this.entCount;
}

Game.initialize = function() {
    this.entities = Array();
    this.effects = Array();
    this.ctx = document.getElementById("canvas").getContext("2d");
    
    this.player = new Player(400, 400)
    this.entities.push(this.player)
    this.cont = true
    this.entCount = 0;
    this.speed_level = 1.0;
    this.points = 0.0;
    this.track_y = 2100;
    this.delta_time = 1/this.fps;
    if (this.music != undefined) { this.music.currentTime = 0; }
    else { this.music = new Audio('sounds/music.mp3'); }
    this.music.play();
    this.music.loop = true;
    this.paused = false;
    this.cheats_enabled = false;
    
    this.player_name = []
    
    for (var i = 0; i < this.generators.length; i++) {
        var gen = this.generators[i];
        gen.time_to_create = (gen.interval[1] - gen.interval[0])*Math.random() + gen.interval[0];
    }
};

///////// DRAW
Game.draw = function() {
    // clear
    this.ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    if (this.track_y < 0) {
        //th = top half;  bh = bottom half
        var thH = Math.abs(this.track_y);
        var bhH = this.track_area.y - thH;
        
        // top half
        this.ctx.drawImage(this.images.track, 0, this.images.track.height-thH, this.images.track.width, thH, 
            this.track_pos.x, this.track_pos.y, this.track_area.x, thH);
        // bottom half
        this.ctx.drawImage(this.images.track, 0, 0, this.images.track.width, bhH, 
            this.track_pos.x, this.track_pos.y+thH, this.track_area.x, bhH);
    }
    else {
        this.ctx.drawImage(this.images.track, 0, this.track_y, this.images.track.width, this.track_area.y, 
            this.track_pos.x, this.track_pos.y, this.track_area.x, this.track_area.y); //destination x,y,w,h
    }
            
    
    this.ctx.fillStyle = 'black';
    this.ctx.fillRect(0, 0, 100, this.track_area.y);
    this.ctx.fillRect(this.track_pos.x + this.track_area.x, 0, 100, this.track_area.y);
    
    this.ctx.fillStyle = '#707070';
    this.ctx.fillRect(this.track_pos.x-3, 0, 3, this.track_area.y);
    this.ctx.fillRect(this.track_pos.x + this.track_area.x, 0, 3, this.track_area.y);
    this.ctx.fillStyle = '#700000';
    this.ctx.fillRect(this.track_pos.x-6, 0, 3, this.track_area.y);
    this.ctx.fillRect(this.track_pos.x + this.track_area.x+3, 0, 3, this.track_area.y);

    this.ctx.fillStyle = 'white';
    this.ctx.font = "18px arial";
    this.ctx.textAlign = 'right';
    this.ctx.fillText(Math.round(this.points), 100-6, 45);
    this.ctx.fillText(this.player.shots_available+"/"+this.player.max_shots, canvas.width, 45);
    this.ctx.fillText(this.player.bombs, canvas.width, 90);
    this.ctx.fillText((this.speed_level*100).toPrecision(4)+'%', canvas.width, 135);
    this.ctx.fillText("Arrow keys", canvas.width, 335);
    this.ctx.fillText("D", canvas.width, 375);
    this.ctx.fillText("S", canvas.width, 415);
    this.ctx.fillText("Space", canvas.width, 455);
    
    var hsY = 150;
    for (var i = 0; i < this.highscores.length; i++) {
        this.ctx.fillText(this.highscores[i].points, 100-6, hsY);
        hsY += 45
    }
    
    this.ctx.textAlign = 'start';
    this.ctx.fillText("Points:", 0, 25);
    this.ctx.fillText("Shots:", canvas.width-100+6, 25);
    this.ctx.fillText("Bombs:", canvas.width-100+6, 70);
    this.ctx.fillText("Speed:", canvas.width-100+6, 115);
    this.ctx.fillStyle = '#A0A000';
    this.ctx.fillText("Movement:", canvas.width-100+6, 315);
    this.ctx.fillText("Fire:", canvas.width-100+6, 355);
    this.ctx.fillText("Use Bomb:", canvas.width-100+6, 395);
    this.ctx.fillText("Pause:", canvas.width-100+6, 435);
    
    this.ctx.fillStyle = 'white';
    this.ctx.fillText("Highscores:", 0, 100);
    this.ctx.fillStyle = '#A0A000';
    var hsY = 130;
    for (var i = 0; i < this.highscores.length; i++) {
        this.ctx.fillText((i+1)+': '+this.highscores[i].name, 0, hsY);
        hsY += 45
    }
    
    //draw elements
    for (var i = 0; i < this.entities.length; i++) {
        this.entities[i].draw(this.ctx)
    }
    
    //draw effects
    for (var i = 0; i < this.effects.length; i++) {
        this.effects[i].draw(this.ctx)
    }
    
    function niceText(str, size, x, y) {
        Game.ctx.fillStyle = 'black';
        Game.ctx.font = size+"px arial";
        Game.ctx.fillText(str, x, y);
        Game.ctx.strokeStyle = 'red';
        Game.ctx.strokeText(str, x, y);
    }
        
    if (this.player.hp <= 0) {
        
        this.ctx.textAlign = 'center';
        niceText("GAME OVER", 40, canvas.width/2, canvas.height/2);
        if (this.getHSindex() >= 0) {
            niceText("Type in highscore name (max 5 chars):", 20, canvas.width/2, canvas.height/2+40);
            niceText(this.player_name.join(""), 30, canvas.width/2, canvas.height/2+70);
        }
        niceText("Press ENTER to start a new game.", 20, canvas.width/2, canvas.height/2+100);
        
        this.ctx.textAlign = 'start';
    }
    else {
        if (this.paused) {
            this.ctx.textAlign = 'center';
            niceText("PAUSED", 40, canvas.width/2, canvas.height/2);
        }
        if (this.player.target != false) {
            Game.ctx.strokeStyle = 'green';
            var tpos = this.player.target.pos.sub(new Vector(10,10));
            var tsize = this.player.target.size.add(new Vector(20,20));
            this.ctx.strokeRect(tpos.x, tpos.y, tsize.x, tsize.y);
        }
    }

};

Game.images = {}
Game.images.explosion1 = new Image();
Game.images.explosion1.src = "images/explosion1.png";
Game.images.explosion2 = new Image();
Game.images.explosion2.src = "images/explosion2.png";
Game.images.explosion3 = new Image();
Game.images.explosion3.src = "images/explosion3.png";
Game.images.explosion4 = new Image();
Game.images.explosion4.src = "images/explosion4.png";
Game.images.explosion5 = new Image();
Game.images.explosion5.src = "images/explosion5.png";
Game.images.explosion6 = new Image();
Game.images.explosion6.src = "images/explosion6.png";
Game.images.bomb_explosion = new Image();
Game.images.bomb_explosion.src = "images/bomb_explosion.png";
Game.images.vehicle_explosion = new Image();
Game.images.vehicle_explosion.src = "images/vehicle_explosion.png";
Game.images.vehicle_collision = new Image();
Game.images.vehicle_collision.src = "images/vehicle_collision.png";
Game.images.dust_cloud = new Image();
Game.images.dust_cloud.src = "images/dust_cloud.png";
Game.images.rock0 = new Image();
Game.images.rock0.src = "images/rock0.png";
Game.images.rock1 = new Image();
Game.images.rock1.src = "images/rock1.png";
Game.images.quicksand = new Image();
Game.images.quicksand.src = "images/quicksand.png";
Game.images.bomb = new Image();
Game.images.bomb.src = "images/bomb.png";
Game.images.bomb_powerup = new Image();
Game.images.bomb_powerup.src = "images/bomb_powerup.png";
Game.images.hp_powerup = new Image();
Game.images.hp_powerup.src = "images/hp_powerup.png";
Game.images.projectile = new Image();
Game.images.projectile.src = "images/projectile.png";
Game.images.track = new Image();
Game.images.track.src = "images/track.png";
Game.images.player = new Image();
Game.images.player.src = "images/player.png";
Game.images.berserker = new Image();
Game.images.berserker.src = "images/berserker.png";
Game.images.slinger = new Image();
Game.images.slinger.src = "images/slinger.png";
Game.images.warrig = new Image();
Game.images.warrig.src = "images/warrig.png";
Game.images.rigturret = new Image();
Game.images.rigturret.src = "images/rigturret.png";

Game.animations = {
explosion1: {
    img: Game.images.explosion1,
    rows: 9,
    cols: 10,
    num_frames: 90,
    fps: 110,
    sw: 100,
    sh: 100
},
explosion2: {
    img: Game.images.explosion2,
    rows: 10,
    cols: 10,
    num_frames: 100,
    fps: 120,
    sw: 100,
    sh: 100
},
explosion3: {
    img: Game.images.explosion3,
    rows: 6,
    cols: 10,
    num_frames: 60,
    fps: 70,
    sw: 100,
    sh: 100
},
explosion4: {
    img: Game.images.explosion4,
    rows: 6,
    cols: 10,
    num_frames: 60,
    fps: 70,
    sw: 100,
    sh: 100
},
explosion5: {
    img: Game.images.explosion5,
    rows: 6,
    cols: 10,
    num_frames: 60,
    fps: 70,
    sw: 100,
    sh: 100
},
explosion6: {
    img: Game.images.explosion6,
    rows: 3,
    cols: 10,
    num_frames: 30,
    fps: 40,
    sw: 100,
    sh: 100
},
bomb_explosion: {
    img: Game.images.bomb_explosion,
    rows: 3,
    cols: 8,
    num_frames: 24,
    fps: 24
},
vehicle_explosion: {
    img: Game.images.vehicle_explosion,
    rows: 4,
    cols: 4,
    num_frames: 16,
    fps: 15
},
vehicle_collision: {
    img: Game.images.vehicle_collision,
    rows: 1,
    cols: 13,
    num_frames: 13,
    fps: 16
},
dust_cloud: {
    img: Game.images.dust_cloud,
    rows: 1,
    cols: 13,
    num_frames: 13,
    fps: 16
},
}

/////// GENERATORS
Game.generators = [
    {name: 'obstacles',
     interval: [10.0, 50.0],
     time_to_create: 0.0,
     enttypes: ['quicksand', 'rock'],
     entchances: [0.6, 0.4],
     entnum: function() {
        return Math.round(Game.speed_level);
     }
    },
    {name: 'obstaclesSimple',
     interval: [1.0, 5.0],
     time_to_create: 0.0,
     enttypes: ['rock'],
     entchances: [1.0],
     entnum: function() { return 1; }
    },
    {name: 'powerups',
     interval: [10.0, 50.0],
     time_to_create: 0.0,
     enttypes: ['powerup'],
     entchances: [1.0],
     entnum: function() {
        return Math.round(Game.speed_level);
     }
    },
    {name: 'berserkers',
     interval: [1.0, 5.0],
     time_to_create: 0.0,
     enttypes: ['berserker'],
     entchances: [1.0],
     entnum: function() {
        return Math.round(Game.speed_level);
     }
    },
    {name: 'slingers',
     interval: [2.0, 8.0],
     time_to_create: 0.0,
     enttypes: ['slinger'],
     entchances: [1.0],
     entnum: function() {
        return Math.round(Game.speed_level);
     }
    },
    {name: 'enemiesSimple',
     interval: [2.0, 12.0],
     time_to_create: 0.0,
     enttypes: ['berserker', 'slinger'],
     entchances: [0.6, 0.4],
     entnum: function() {
        return 2*Math.floor(Game.speed_level);
     }
    },
    {name: 'allenemies',
     interval: [10.0, 30.0],
     time_to_create: 0.0,
     enttypes: ['berserker', 'slinger', 'warrig'],
     entchances: [0.4, 0.4, 0.2],
     entnum: function() {
        return 2*Math.floor(Game.speed_level);
     }
    },
    {name: 'rigs',
     interval: [60.0, 60.0],
     time_to_create: 0.0,
     enttypes: ['warrig'],
     entchances: [1.0],
     entnum: function() {
        return Math.round(Game.speed_level) - 1;
     }
    },
];
Game.entityFactory = {
'berserker': Berserker,
'slinger': Slinger,
'warrig': WarRig,
'rock': Rock,
'quicksand': QuickSand,
'powerup': function(x, y) {
    return RandomizePowerUp(new Vector(x,y), 1.0);
}
};
///////// UPDATE
Game.update = function() {
    /*debugging feature to run SUPER!HOT! (frame-per-frame)*/
    //if (!this.cont) return;
    //this.cont = false;

    var dt = 1.0/this.fps;
    this.delta_time = dt;
    
    if (this.player.hp > 0 && !this.paused) {
        // generate new entities
        var possibleBottomEntTypes = ['berserker', 'slinger'];
        for (var i = 0; i < this.generators.length; i++) {
            var gen = this.generators[i];
            gen.time_to_create -= dt;
            if (gen.time_to_create <= 0) {
                var n = gen.entnum();
                //console.log('Executing generator '+gen.name+', n='+n);
                for (; n > 0; n--) {
                    var entIndex = Math.random();
                    var cumulative = 0.0;
                    for (var j = 0; j < gen.enttypes.length; j++) {
                        var type = gen.enttypes[j]
                        var chance = gen.entchances[j];
                        if (entIndex < chance + cumulative) {
                            var factory = this.entityFactory[type];
                            var X = Math.random()*this.track_area.x;
                            var Y = -10;
                            if (Math.random()<0.25 && isInArray(type, possibleBottomEntTypes)) {
                                Y = this.track_area.y-50;
                            }
                            this.entities.push(new factory(X+this.track_pos.x, Y+this.track_pos.y));
                            if (type == 'warrig') //special case...
                                this.entities[this.entities.length-1].createTurrets()
                            //console.log("Generating entity "+type);
                            break;
                        }
                        cumulative += chance;
                    }
                }
                gen.time_to_create = (gen.interval[1] - gen.interval[0])*Math.random() + gen.interval[0];
                //console.log('Finished generator. New TTC = '+gen.time_to_create);
                break
            }
        }
    
        // check for collision & handle them
        for (var i = 0; i < this.entities.length; i++) {
            for (var j = i+1; j < this.entities.length; j++) {
                var ent1 = this.entities[i];
                var ent2 = this.entities[j];
                if (ent1.checkCollision(ent2)) {
                    ent1.collidedWith(ent2);
                }
            }
        }

        // update each entity
        this.entities.forEach(function(ent) {
            ent.update(dt);
            ent.stuck = false;
            if (ent.hp <= 0) {
                ent.onDeath();
                Game.points += ent.point_value;
                Game.entities.splice(Game.entities.indexOf(ent), 1);
            }
        });
        
        // update each effect
        this.effects.forEach(function(eff) {
            eff.update(dt);
            if (eff.destroyed) {
                Game.effects.splice(Game.effects.indexOf(eff), 1);
            }
        });
        
        // update game stats
        this.points += dt; //+1 point per second
        this.speed_level += dt/60; //speed_level will increase by 1 each 60 secs
        
        this.track_y -= this.speed_level + 5;
        if (this.track_y <= -700) {
            this.track_y = 2100;
        }
    }
};

///////// INPUT
Game.inputDown = function(e) {
    if (this.player.hp <= 0) return;
    var code = e.keyCode
    /* left = 37; up = 38; right = 39; down = 40 */
    if (this.cheats_enabled) {
        if (code == 79) {
            this.entities.push( new Berserker(200, 200) )
        }
        else if (code == 73) { 
            this.entities.push( new Slinger(600, 200) )
        }
        else if (code == 85) { 
            this.entities.push( new WarRig(400, 160) )
            this.entities[this.entities.length-1].createTurrets()
        }
        else if (code == 82) { 
            this.entities.push( new Rock(Math.random()*canvas.width, 0) );
        }
        else if (code == 69) { 
            this.entities.push( new QuickSand(Math.random()*canvas.width, 0) );
        }
    }
    
    this.cont = true;
        
    this.player.input(code, true)
}
Game.inputUp = function(e) {
    var code = e.keyCode
    
    if (this.player.hp <= 0) {
        if (code >= 65 && code <= 90 && this.player_name.length < 5) { //A-Z
            this.player_name.push(String.fromCharCode(code));
        }
        else if (code == 8) { //backspace
            this.player_name.pop();
        }
        else if (code == 13) { //enter
            if (this.player_name.length == 0)   this.player_name = ['?','?','?'];
            var hs_index = this.getHSindex();
            if (hs_index >= 0) {
                this.highscores.pop();
                this.highscores.splice(hs_index, 0, {name: this.player_name.join(""), points: Math.round(this.points)});
            }
            Game.initialize();
        }
    }
    else {
        if (code == 32) {
            //pause game
            this.paused = !this.paused;
        }
        if (!this.paused) {
            this.player.input(code, false);
        }
    }
}

Game.getHSindex = function() {
    var hs_index = -1;
    for (var i = 0; i < this.highscores.length; i++) {
        if (this.points > this.highscores[i].points) {
            hs_index = i;
            break;
        }
    }
    return hs_index;
}


/******************************** ENTITIES ************************************/
function BaseCar(type, x, y, w, h, color, speed, hp, points) {
this.type = type;
this.pos = new Vector(x,y);
this.size = new Vector(w,h);
this.color = color;
this.img = Game.images[type];
this.base_speed = speed;
this.stuck = false; //if caught on quicksand
this.hp = hp;
this.max_hp = hp;
this.show_life_bar = true;
this.ID = Game.getIDfor(this);
this.point_value = points;
this.last_moved_dir = new Vector(0,0);
this.considers_game_speed = false;

this.draw = function(ctx) {
    this.drawEntity(ctx);
    this.drawHPBar(ctx);
}
this.drawEntity = function(ctx) {
    /*if (this.img != undefined ) {
        ctx.drawImage(this.img, 0, 0, this.img.width, this.img.height, 
            this.pos.x, this.pos.y, this.size.x, this.size.y); //destination x,y,w,h
    }
    else {
        ctx.fillStyle = this.color
        ctx.fillRect(this.pos.x, this.pos.y, this.size.x, this.size.y)
    }*/
    var w = this.size.x;
    var h = this.size.y;
    var x = this.pos.x + w/2;
    var y = this.pos.y + h/2;
    var angle = this.last_moved_dir.x*Math.PI/8;
    if (this.type == 'warrig')  angle = 0.0;
    
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.drawImage(this.img, -w / 2, -h / 2, w, h);
    ctx.rotate(-angle);
    ctx.translate(-x, -y);
}
this.drawHPBar = function(ctx) {
    if (this.show_life_bar) {
        ctx.fillStyle = 'black'
        ctx.fillRect(this.pos.x, this.pos.y+this.size.y+1, this.size.x, 5)
        ctx.fillStyle = 'red'
        ctx.fillRect(this.pos.x, this.pos.y+this.size.y+1, this.size.x*this.hp/this.max_hp, 5)
    }
}

this.checkCollision = function(ent) {
    var notIntersects = this.pos.x > (ent.pos.x + ent.size.x) ;
    notIntersects = notIntersects || (this.pos.x + this.size.x) < ent.pos.x ;
    notIntersects = notIntersects || this.pos.y > (ent.pos.y + ent.size.y) ;
    notIntersects = notIntersects || (this.pos.y + this.size.y) < ent.pos.y ;
    return !notIntersects
}

this.limitInRect = function(pos, size) {
    var center = this.pos.add(this.size.scale(0.5))
    var moved = false;
    if (center.x < pos.x) {
        this.pos.x = pos.x - this.size.x/2
        moved = true;
    }
    else if (center.x > pos.x + size.x) {
        this.pos.x = pos.x + size.x - this.size.x/2
        moved = true;
    }
    if (center.y < pos.y) {
        this.pos.y = pos.y - this.size.y/2
        moved = true;
    }
    else if (center.y > pos.y + size.y) {
        this.pos.y = pos.y + size.y - this.size.y/2
        moved = true;
    }
    return moved
}

this.center = function() {
    return this.pos.add(this.size.scale(0.5));
}

this.onDeath = function() {}

this.speed = function() {
    var s = this.base_speed;
    if (this.considers_game_speed) {
        s = s * Game.speed_level + 5;
    }
    return s * (1.0 - this.stuck*0.85); //0.85 is % of speed lost while stuck
}

this.move = function(dir) {
    this.last_moved_dir = dir.copy();
    this.pos = this.pos.add(dir.scale(this.speed()))
    return this.limitInRect(Game.track_pos, Game.track_area)
}

}//end prototype BaseCar

/************* Player ****************/
function Player(x, y) {
BaseCar.call(this, 'player', x, y, 32, 60, 'black', 4, 150, 0);
this.desired_move = new Vector(0,0);
this.bombs = 3;
this.max_shots = 25;
this.shots_available = this.max_shots;
this.shot_reload_time = 0.2;
this.cooldown_time = 0.1;
this.cooldown_elapsed = this.cooldown_time;
this.reload_elapsed = 0.0;
this.target = false;
this.shot_dmg = 20;
this.shot_speed = 15;
this.try_fire = false;

this.draw = function(ctx) {
    this.drawEntity(ctx);
    this.drawHPBar(ctx);
    var img = Game.images.rigturret;
    var w = this.size.x*0.6;
    var h = w * img.height / img.width;
    var xoffset = (this.size.x - w)/2;
    var yoffset = this.size.y/2 - h/2;
    var x = this.pos.x + xoffset + w/2;
    var y = this.pos.y + yoffset + h/2;
    var angle = 0.0;
    if (this.target != false) {
        var dir = this.target.center().sub(this.center());
        dir.normalize();
        angle = Math.atan2(dir.y, dir.x)+Math.PI/2;
    }
    
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.drawImage(img, -w / 2, -h / 2, w, h);
    ctx.rotate(-angle);
    ctx.translate(-x, -y);
}

this.update = function(dt) {
    var moveDelta = this.desired_move.copy()
    moveDelta.normalize()
    this.move(moveDelta);
    CreateVehicleDustCloud(this);
    
    if (this.shots_available < this.max_shots) {
        this.reload_elapsed += dt;
        if (this.reload_elapsed > this.shot_reload_time) {
            this.reload_elapsed = 0.0;
            this.shots_available += 1;
        }
    }
    
    this.target = false;
    var min_dist = Game.track_area.len()
    var validTargets = ['berserker', 'slinger', 'warrig', 'rigturret']
    for (i = 1; i < Game.entities.length; i++) {
        var ent = Game.entities[i]
        if (ent.hp <= 0 || !isInArray(ent.type, validTargets))
            continue;
        var dist = ent.center().sub(this.center())
        if (dist.len() < min_dist) { //yay raizes desnecessarias!
            min_dist = dist.len();
            this.target = ent;
        }
    }
    
    this.cooldown_elapsed += dt;
    if (this.target != false && this.try_fire && this.cooldown_elapsed >= this.cooldown_time && this.shots_available > 0) {
        var dir = this.target.center().sub(this.center());
        dir.normalize();

        var init_pos = this.center();
        var projectile = new Projectile(init_pos.x, init_pos.y, this.shot_dmg, this.shot_speed, dir, 2);
        projectile.cant_hit.push(this.type);
        Game.entities.push(projectile);
        this.shots_available -= 1;
        this.reload_elapsed = 0.0;
        this.cooldown_elapsed = 0.0;
    }
}

this.input = function(code, isDown) {
    //cheats
    if (Game.cheats_enabled) {
        if (code == 72) {
            this.hp = this.max_hp
        }
        if (code == 66) {
            this.bombs += 1;
        }
    }
    //////
    if (code == 37 && (isDown || (!isDown && this.desired_move.x == -1))) { //left 
        this.desired_move.x = -1*isDown
    }
    else if (code == 38 && (isDown || (!isDown && this.desired_move.y == -1))) { //up
        this.desired_move.y = -1*isDown
    }
    else if (code == 39 && (isDown || (!isDown && this.desired_move.x == 1))) { //right
        this.desired_move.x = 1*isDown
    }
    else if (code == 40 && (isDown || (!isDown && this.desired_move.y == 1))) { //down
        this.desired_move.y = 1*isDown
    }
    else if (code == 68) {
        // shoot back!
        this.try_fire = isDown;
    }    
    else if (code == 83 && !isDown && this.bombs > 0) {
        // release bomb
        this.bombs -= 1;
        var bomb = new Bomb(this.pos.x, this.pos.y, 1);
        Game.entities.push(bomb);
    }
}

this.collidedWith = function(ent) {
    ent.collidedWith(this);
}

this.onDeath = function() {
    CreateVehicleExplosion(this);
}
}//end prototype Player

/*********** Berserker ******************/
function Berserker(x, y) { 
BaseCar.call(this, 'berserker', x, y, 32, 60, 'red', 3.5, 25, 200);
this.isChasing = true;
this.moveAwayElapsed = 0.0

this.update = function(dt) {
    var dir = Game.player.center().sub(this.center());
    dir.normalize();
    if (!this.isChasing) {
        dir = dir.scale(-1);
        this.moveAwayElapsed += dt
        if (this.moveAwayElapsed > 0.7) {
            this.isChasing = true;
            this.moveAwayElapsed = 0.0
        }
    }
    this.move(dir);
    CreateVehicleDustCloud(this);
}

this.collidedWith = function(ent) {
    if (ent.type == 'player') {
        ent.hp -= 20;
        this.hp -= 5;
        this.isChasing = false
    }
    else if (ent.type == 'berserker') {
        ent.hp -= 0.5;
        this.hp -= 0.5;
    }
    else {
        ent.collidedWith(this);
        return;
    }
    CreateVehicleCollision(this, ent);
    var dir = this.center().sub(ent.center());
    dir.normalize();
    this.pos = this.pos.add(dir.scale(2*this.speed()));
}

this.onDeath = function() {
    CheckAndDropPowerUp(this.pos, 0.10);
    CreateVehicleExplosion(this);
}
}//end prototype Berserker

/*********** Slinger ******************/
function Slinger(x, y) { 
BaseCar.call(this, 'slinger', x, y, 32, 60, 'purple', 2, 25, 200);
this.time_to_shoot = 0.7
this.cooldown = 0.0
this.range = Math.random()*200 + 100 //range in [100, 300]

this.update = function(dt) {
    var dir = Game.player.center().sub(this.center());
    var dist = dir.len()
    dir.normalize();
    
    if (Math.abs(dist - this.range) > 30) {
        var move_target = Game.player.pos.add(dir.scale(-this.range))
        var move_dir = move_target.sub(this.pos)
        move_dir.normalize()
        this.move(move_dir);
    }
    else {
        this.last_moved_dir = new Vector(0,0);
    }
    CreateVehicleDustCloud(this);
    
    this.cooldown += dt
    if (this.cooldown > this.time_to_shoot) {
        //SHOOT!
        var init_pos = this.center();
        var projectile = new Projectile(init_pos.x, init_pos.y, 6, 15, dir, 2);
        projectile.cant_hit.push(this.type);
        Game.entities.push(projectile);
        this.cooldown = 0.0;
    }
}

this.draw = function(ctx) {
    this.drawEntity(ctx);
    this.drawHPBar(ctx);
    var img = Game.images.rigturret;
    var w = this.size.x*0.6;
    var h = w * img.height / img.width;
    var xoffset = (this.size.x - w)/2;
    var yoffset = this.size.y/2 - h/2;
    var x = this.pos.x + xoffset + w/2;
    var y = this.pos.y + yoffset + h/2;
    var dir = Game.player.center().sub(this.center());
    dir.normalize();
    var angle = Math.atan2(dir.y, dir.x)+Math.PI/2;
    
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.drawImage(img, -w / 2, -h / 2, w, h);
    ctx.rotate(-angle);
    ctx.translate(-x, -y);
}

this.collidedWith = function(ent) {
    if (ent.type == 'player') {
        ent.hp -= 1;
        this.hp -= 20;
        this.cooldown -= this.time_to_shoot/3;
    }
    else if (ent.type == 'berserker') {
        ent.hp -= 0.5;
        this.hp -= 8;
    }
    else if (ent.type == 'slinger') {
        ent.hp -= 0.5;
        this.hp -= 0.5;
    }
    else {
        ent.collidedWith(this);
        return;
    }
    CreateVehicleCollision(this, ent);
    var dir = this.pos.sub(ent.pos);
    dir.normalize();
    this.pos = this.pos.add(dir.scale(2*this.speed()));
}

this.onDeath = function() {
    CheckAndDropPowerUp(this.pos, 0.15);
    CreateVehicleExplosion(this);
}
}//end prototype Slinger

/*********** WarRig ******************/
function WarRig(x, y) { 
BaseCar.call(this, 'warrig', x, y, 40, 160, 'yellow', 1, 300, 1000);
this.time_to_shoot = 1.0
this.cooldown = 0.0

this.createTurrets = function() {
    Game.entities.push(new RigTurret(this, 50))
    Game.entities.push(new RigTurret(this, 100))
}

this.update = function(dt) {
    var firing_pos = this.pos.add(this.size.scale2(0.5, 0.16))
    var dir = Game.player.center().sub(firing_pos);
    var dist = dir.len()
    dir.normalize();
    
    var lastPos = this.pos.copy();
    this.move(dir);
    CreateVehicleDustCloud(this);
    var posDiff = this.pos.sub(lastPos);
    
    this.cooldown += dt
    if (this.cooldown > this.time_to_shoot) {
        //SHOOT!
        var init_pos = firing_pos;
        var projectile = new Projectile(init_pos.x, init_pos.y, 10, 15, dir, 2);
        projectile.cant_hit.push(this.type);
        projectile.cant_hit.push('rigturret');
        Game.entities.push(projectile);
        this.cooldown = 0.0;
    }
}

this.collidedWith = function(ent) {
    if (ent.type == 'player') {
        ent.hp -= 25;
        this.hp -= 0.5;
        this.cooldown -= this.time_to_shoot/3;
    }
    else if (ent.type == 'berserker' || ent.type == 'slinger') {
        ent.hp -= 1;
        this.hp -= 0.5;
    }
    else if (ent.type == 'rigturret')
        return
    else if (ent.type == 'warrig') {
    }
    else {
        ent.collidedWith(this);
        return;
    }
    CreateVehicleCollision(this, ent);
    var dir = ent.pos.sub(this.pos);
    dir.normalize();
    ent.pos = ent.pos.add(dir.scale(2*this.speed()));
}

this.onDeath = function() {
    CheckAndDropPowerUp(this.pos, 1.0);
    CreateVehicleExplosion(this);
}

}//end prototype WarRig

/*********** RigTurret ******************/
function RigTurret(rig, yoffset) { 
BaseCar.call(this, 'rigturret', rig.pos.x, rig.pos.y+yoffset, 40, 40, '#808000', 0, 40, 100);
this.time_to_shoot = 0.5
this.cooldown = 0.0
this.show_life_bar = false;
this.yoffset = yoffset;
this.rig = rig

this.draw = function(ctx) {
    var img = Game.images.rigturret;
    var w = this.size.x*0.75;
    var h = w * img.height / img.width;
    var xoffset = (this.size.x - w)/2;
    var yoffset = this.size.y/2 - h/2;
    var x = this.pos.x + xoffset + w/2;
    var y = this.pos.y + yoffset + h/2;
    var dir = Game.player.center().sub(this.center());
    dir.normalize();
    var angle = Math.atan2(dir.y, dir.x)+Math.PI/2;
    
    ctx.translate(x, y);
    ctx.rotate(angle);
    ctx.drawImage(img, -w / 2, -h / 2, w, h);
    ctx.rotate(-angle);
    ctx.translate(-x, -y);
}

this.update = function(dt) {
    if (rig == undefined || rig.hp <= 0) {
        this.hp = -1;
        return;
    }
    this.pos = rig.pos.add(new Vector(0, this.yoffset));

    this.cooldown += dt
    if (this.cooldown > this.time_to_shoot) {
        //SHOOT!
        var init_pos = this.center();
        var dir = Game.player.center().sub(init_pos);
        dir.normalize();
        var projectile = new Projectile(init_pos.x, init_pos.y, 5, 15, dir, 2);
        projectile.color = '#000080'
        projectile.cant_hit.push(this.type);
        projectile.cant_hit.push('warrig');
        Game.entities.push(projectile);
        this.cooldown = 0.0;
    }
}

this.collidedWith = function(ent) {
    if (ent.type == 'player') {
        this.hp -= 5;
        this.cooldown -= this.time_to_shoot/3;
    }
    else if (ent.type == 'berserker' || ent.type == 'slinger') {
        ent.hp -= 1;
        this.hp -= 0.5;
    }
    else if (ent.type == 'warrig' || ent.type == 'rigturret')
        return
    else {
        ent.collidedWith(this);
        return;
    }
    CreateVehicleCollision(this, ent);
    var dir = ent.pos.sub(this.pos);
    dir.normalize();
    ent.pos = ent.pos.add(dir.scale(2*this.speed()));
}

this.onDeath = function() {
    CheckAndDropPowerUp(this.pos, 0.15);
    CreateVehicleExplosion(this);
}
}//end prototype RigTurret

/*********** Projectile ******************/
function Projectile(x, y, dmg, speed, dir, lifetime) { 
BaseCar.call(this, 'projectile', x, y, 7, 7, 'blue', speed, 1, 0);
this.dmg = dmg;
this.dir = dir.copy();
this.lifetime = lifetime;
this.show_life_bar = false;
this.cant_hit = ['projectile', 'bomb', 'powerup', 'quicksand'];
var fireSound = new Audio("sounds/fire.wav");
fireSound.volume = 0.4;
fireSound.play();

this.update = function(dt) {
    this.lifetime -= dt;
    if (this.lifetime < 0.0 || this.move(this.dir)) {
        this.hp = -1;
    }
}

this.collidedWith = function(ent) {
    if (isInArray(ent.type, this.cant_hit)) return;
    this.hp = -1;
    ent.hp -= this.dmg;
    var hit_sounds = ['explosion', 'hit1', 'hit2', 'hit3', 'hit4'];
    (new Audio("sounds/hit"+(1+Math.floor(Math.random()*5))+".wav")).play();
    CreateExplosionAt(this, 20, 1, Game.animations['explosion'+(1+Math.floor(Math.random()*5))]);
    if (ent.type != 'player') {
        //this means it is a projectile that hit something other than the player
        //meaning, player projectile hit enemy, or enemy shooting themselves, 
        //either way...
        this.point_value = 10;
    }
    //console.log(this.type+' '+this.ID+' hitting '+ent.type+' '+ent.ID+' at '+ent.pos);
}

}//end prototype Projectile

/*********** Bomb ******************/
function Bomb(x, y, speed) { 
BaseCar.call(this, 'bomb', x, y, 30, 30, 'purple', speed, 1, 0);
this.dmg = 100;
this.blast_radius = 140;
this.dir = new Vector(0, 1);
this.show_life_bar = false;
this.cant_hit = ['player', 'projectile', 'bomb', 'powerup', 'quicksand']; //bomb projectile doesnt hit
this.cant_dmg = ['player', 'powerup']; //bomb area dmg does not apply
this.considers_game_speed = true;
this.lifetime = 1.0;

this.draw = function(ctx) {
    this.drawEntity(ctx);
    
    ctx.textAlign = 'center';
    ctx.fillText(this.lifetime.toPrecision(2), this.center().x, this.center().y+this.size.y/2);
}

this.update = function(dt) {
    this.lifetime -= dt;
    if (this.move(this.dir)) {
        this.hp = -1;
    }
    if (this.lifetime <= 0) {
        this.explode();
    }
}

this.collidedWith = function(ent) {
    if (isInArray(ent.type, this.cant_hit)) return;
    this.point_value = 150;
    this.explode();
}

this.explode = function() {
    this.hp = -1;
    CreateExplosionAt(this, this.blast_radius*2, 1, Game.animations.bomb_explosion);
    (new Audio("sounds/bomb_explosion.mp3")).play();
    for (var i = 0; i < Game.entities.length; i++) {
        var ent = Game.entities[i];
        if (!isInArray(ent.type, this.cant_dmg)) {
            var dist = ent.center().sub(this.center());
            if (dist.len() <= this.blast_radius) {
                if (ent.type == 'bomb' && ent.hp > 0) {
                    ent.explode();
                }
                ent.hp -= this.dmg;
                //console.log('Bomb '+this.ID+' damaging '+ent.type+' '+ent.ID);
            }
        }
    }
}

}//end prototype Bomb

/*********** PowerUp ******************/
function PowerUp(x, y, action) { 
BaseCar.call(this, 'powerup', x, y, 30, 30, 'green', 0.0, 1, 0);
this.dir = new Vector(0, 1);
this.show_life_bar = false;
this.was_picked_up = false;
this.onPickup = action
this.considers_game_speed = true;

this.update = function(dt) {
    if (this.move(this.dir)) {
        this.hp = -1;
    }
}

this.collidedWith = function(ent) {
    if (ent.type != 'player')
        return
    this.was_picked_up = true;
    this.hp = -1;
}

this.onDeath = function() { 
    if (this.was_picked_up) {
        this.onPickup();
        this.point_value = 50;
    }
}

}//end prototype PowerUp

var PowerUpTable = [
{'name': 'hpup',
 'chance': 0.65,
 'image': Game.images.hp_powerup,
 'action': function() {
    Game.player.hp += 150;
    if (Game.player.hp > Game.player.max_hp)
        Game.player.hp = Game.player.max_hp;
    //console.log("got hp up")
 }
},
{'name': 'bombup',
 'chance': 0.35,
 'image': Game.images.bomb_powerup,
 'action': function() {
    Game.player.bombs += 1;
    //console.log("got bomb up")
 }
},
]

function CheckAndDropPowerUp(pos, chanceToCreate) {
    //console.log('checking for power dropping')
    var pup = RandomizePowerUp(pos, chanceToCreate);
    if (pup != false) {
        Game.entities.push(pup);
    }
}
function RandomizePowerUp(pos, chanceToCreate) {
    //console.log('checking for power dropping')
    if (Math.random() <= chanceToCreate) {
        var itemIndex = Math.random();
        var cumulative = 0.0;
        for (var i = 0; i < PowerUpTable.length; i++) {
            var powerUpData = PowerUpTable[i];
            if (itemIndex < powerUpData.chance + cumulative) {
                var pup = new PowerUp(pos.x, pos.y, powerUpData.action);
                pup.img = powerUpData.image;
                return pup;
            }
            cumulative += powerUpData.chance;
        }
    }
    return false;
}

/*********** Rock ******************/
function Rock(x, y) { 
BaseCar.call(this, 'rock', x, y, 60, 60, 'black', 1, 1000, 5);
this.dir = new Vector(0, 1);
this.show_life_bar = false;
this.considers_game_speed = true;
this.img = Game.images['rock'+Math.round(Math.random())];
this.size.y = this.size.x * this.img.height / this.img.width;
this.should_explode = true;

this.update = function(dt) {
    if (this.move(this.dir)) {
        this.hp = -1;
        this.should_explode = false;
    }
}

this.collidedWith = function(ent) {
    if (ent.type == 'rock' || ent.type == 'quicksand') return;
    ent.hp = -1; //K.O.!
    CreateVehicleCollision(this, ent);
}

this.onDeath = function() {
    if (this.should_explode) {
        CheckAndDropPowerUp(this.pos, 1);
        CreateVehicleExplosion(this);
    }
}
}//end prototype Rock

/*********** QuickSand ******************/
function QuickSand(x, y) { 
BaseCar.call(this, 'quicksand', x, y, 40, 40, '#906000', 1, 1000, 5);
this.dir = new Vector(0, 1);
this.show_life_bar = false;
this.considers_game_speed = true;
this.should_explode = true;

this.update = function(dt) {
    if (this.move(this.dir)) {
        this.hp = -1;
        this.should_explode = false;
    }
}

this.collidedWith = function(ent) {
    if (ent.type == 'rock' || ent.type == 'quicksand' || ent.type == 'projectile') return;
    if (!ent.stuck)
        ent.pos = ent.pos.add(this.dir.scale(this.speed()*0.8));
    ent.stuck = true;
}

this.onDeath = function() {
    if (this.should_explode) {
        CheckAndDropPowerUp(this.pos, 1);
        CheckAndDropPowerUp(this.pos, 1);
        CreateVehicleCollision(this, this);
    }
}
}//end prototype QuickSand

/******************************** EFFECTS ************************************/
function Explosion(pos, size, speed, type) {
this.pos = pos.copy();
this.base_speed = speed;
this.size = new Vector(size,size);
this.destroyed = false;
this.dir = new Vector(0, 1);

this.type = type;
this.frame_index = 0;
this.elapsed = 0.0;
if (type.sw != undefined) { this.sw = type.sw; }
else { this.sw = type.img.width / this.type.cols; }
if (type.sh != undefined) { this.sh = type.sh; }
else { this.sh = type.img.height / this.type.rows; }

this.update = function(dt) {
    this.pos = this.pos.add(this.dir.scale(this.speed()));
    
    if (this.elapsed > 1 / this.type.fps) {
        this.elapsed = 0.0;
        this.frame_index++;
    }
    this.elapsed += dt;
    
    if (this.limitInRect(Game.track_pos, Game.track_area) || this.frame_index >= this.type.num_frames) {
        this.destroyed = true;
    }
}
this.draw = function(ctx) {
    //ctx.fillStyle = 'white';
    var sx = (this.frame_index % this.type.cols) * this.sw;
    var sy = Math.floor(this.frame_index / this.type.cols) * this.sh;
    ctx.drawImage(this.type.img, sx, sy, this.sw, this.sh, 
        this.pos.x, this.pos.y, this.size.x, this.size.y); //destination x,y,w,h
}

this.limitInRect = function(pos, size) {
    var center = this.center();
    var moved = false;
    if (center.x < pos.x) {
        this.pos.x = pos.x - this.size.x/2
        moved = true;
    }
    else if (center.x > pos.x + size.x) {
        this.pos.x = pos.x + size.x - this.size.x/2
        moved = true;
    }
    if (center.y < pos.y) {
        this.pos.y = pos.y - this.size.y/2
        moved = true;
    }
    else if (center.y > pos.y + size.y) {
        this.pos.y = pos.y + size.y - this.size.y/2
        moved = true;
    }
    return moved
}

this.center = function() {
    return this.pos.add(this.size.scale(0.5));
}

this.speed = function() {
    var s = this.base_speed * Game.speed_level + 5;
    return s;
}

}//end prototype Explosion
function CreateExplosion(pos, size, speed, type) {
    Game.effects.push( new Explosion(pos, size, speed, type) );
}
function CreateExplosionAt(ent, size, speed, type) {
    CreateExplosion(ent.center().sub(new Vector(size/2, size/2)), size, speed, type);
}

function CreateVehicleExplosion(ent) {
    CreateExplosionAt(ent, ent.size.len()*2, 1, Game.animations.vehicle_explosion);
    (new Audio("sounds/vehicle_explosion.mp3")).play();
}
function CreateVehicleCollision(ent1, ent2) {
    var pos = ent1.center().add(ent2.center().sub(ent1.center()).scale(0.5));
    var size = (ent1.size.len()+ent2.size.len())/2;
    pos = pos.sub(new Vector(size/2, size/2));
    CreateExplosion(pos, size, 1, Game.animations.vehicle_collision);
    (new Audio("sounds/collision"+(1+Math.floor(Math.random()*4))+".wav")).play();
}
function CreateVehicleDustCloud(ent) {
    var pos = ent.pos.add(ent.size.scale2(-0.5,1));
    var size = ent.size.x*2;
    pos = pos.sub(new Vector(0, size*0.5));
    if (ent.dusttimer == undefined || ent.dusttimer > 0.1) {
        CreateExplosion(pos, size, 1, Game.animations.dust_cloud);
        ent.dusttimer = 0.0;
    }
    else
        ent.dusttimer += Game.delta_time;
}

/*********************************** UTILITIES *********************************/
function Vector(x, y) {
this.x = x
this.y = y

this.add = function(v) {
    return new Vector(this.x + v.x, this.y + v.y)
}
this.neg = function() {
    return new Vector(-this.x, -this.y)
}
this.sub = function(v) {
    return new Vector(this.x - v.x, this.y - v.y)
}
this.squaredLen = function() {
    return Math.pow(this.x, 2) + Math.pow(this.y, 2)
}
this.len = function() {
    return Math.sqrt(this.squaredLen())
}
this.normalize = function() {
    var l = this.len()
    if (l > 0) {
        this.x = this.x / l
        this.y = this.y / l
    }
}
this.copy = function() {
    return new Vector(this.x, this.y);
}
this.scale = function(s) {
    return new Vector(this.x*s, this.y*s)
}
this.scale2 = function(s1, s2) {
    return new Vector(this.x*s1, this.y*s2)
}
this.toString = function() {
    return "("+this.x+", "+this.y+")"
}
}//end prototype Vector

function isInArray(value, array) {
  return array.indexOf(value) > -1;
}


/* REQUISITOS:
(1) carro se move lateralmente na pista
(2) desviar de obstaculos (nunca de forma impossivel a ser desviada)
(3) objetivo ir mais longe (contar tempo ou pontuação)
(4) deve ser mostrado um high score (desde q a página foi aberta)
(5) input: setas no teclado
(6) cenário/pista se movimentar de cima p/ baixo, com sensação de velocidade
(7) velocidade inicial baixa e ir aumentando, junto com a dificuldade
(8) pelo menos 3 obstáculos diferentes, com gráficos e efeitos diferentes
(9) carro do jogador e carros obstaculos devem ter grafico/animacao indicando direcao(normal) e colisão.
========================================================================================================
   IDEIA
----------------
-highscore por pontos
-pontos: distancia percorrida + coisas feitas (inimigos destruidos, por exemplo)
-carros tem vida
-INIMIGOS:
    -Berserker: carros te perseguem pra bater em vc, podem inclusive vir pro trás
    -Slinger: carros tentam atirar explosivos em vc, a uma certa distância
    -War Rig: grande carro tanque, pode tentar bater ou atirar. de preferência ter sub-alvos/estágios, por exemplo: atirador1, atirador2, motorista,
        e matando atiradores ele para de atirar, matando motorista da mais dano no veiculo, pra destrui-lo
-OBSTACULOS
    -Pedras: on-hit is dead!
    -QuickSand: uma área, enquanto passa vc perde mobilidade
-EXPLOSIONS?!?
-quando morrer, um carro pode:
    -simplesmente explodir (dar dano perto?)
    -motorista morre, ele anda um pouco a esmo podendo bater em outros e explode
-talvez fazer com que inimigos possam ter uma chance (dependendo de qual inimigo eh)
 de dropar um power-up pra curar hp do player
 
 ------------
 EFEITOS (grafico+som)
 ------------
 -impacto de tiro (explosaozinha): grafico ok, som ok
 -impacto de veiculos/obstaculos: grafico ok, som ok
 -explosao bomba: grafico ok, som ok
 -explosao veiculos: grafico ok, som ok
 -fumaca/areia (dust cloud) de movimento de veiculos: OK
 
 ------------
 GRAFICOS
 ------------
 -player: OK
 -berserker: OK
 -slinger: OK
 -warrig: OK
 -turret: OK (tanto na rig, qto no slinger e player, e rotacionando)
 -powerup: OK
 -bomba: OK
 -projetil: OK
 -rock: OK
 -quicksand: OK
 -background/track: OK
*/