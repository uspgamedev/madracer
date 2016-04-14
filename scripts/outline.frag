uniform sampler2D texture;
uniform vec2 stepSize;
uniform vec4 outlineColor;

void main()
{
    //number alpha = 4*texture2D( texture, texturePos ).a;
    float alpha = 4 * texture2D(texture, gl_TexCoord[0].xy).a;
    alpha -= texture2D( texture, gl_TexCoord[0].xy + vec2( stepSize.x, 0.0 ) ).a;
    alpha -= texture2D( texture, gl_TexCoord[0].xy + vec2( -stepSize.x, 0.0 ) ).a;
    alpha -= texture2D( texture, gl_TexCoord[0].xy + vec2( 0.0, stepSize.y ) ).a;
    alpha -= texture2D( texture, gl_TexCoord[0].xy + vec2( 0.0, -stepSize.y ) ).a;
    alpha = abs(alpha);
    
    vec4 pixel = gl_Color * texture2D(texture, gl_TexCoord[0].xy);
    
    gl_FragColor = (pixel.a>0.5)*pixel + (pixel.a < 0.5)*vec4(outlineColor.r, outlineColor.g, outlineColor.b, alpha);
}
