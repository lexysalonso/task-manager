import { Link } from "react-router-dom";
import { Button } from "@/presentation/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/presentation/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/presentation/components/ui/avatar";
import { useAuthStore } from "@/application/store/auth.store";
import { useLogout } from "@/application/hooks/use-auth";
import { User } from "lucide-react";
import { decodeTokenPayload } from "@/lib/jwt";
import { getInitials } from "@/lib/utils";

export function Navbar() {
  const token = useAuthStore((s) => s.token);
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();

  const fallbackUser = !user && token ? decodeTokenPayload(token) : null;
  const displayName = user?.full_name || (fallbackUser?.email as string) || null;
  const displayEmail = user?.email || (fallbackUser?.email as string) || null;
  const initials = getInitials(displayName);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/projects" className="flex items-center gap-2 font-bold text-xl">
          Gestor de Tareas
        </Link>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="relative h-10 w-10 rounded-full" aria-label="Menú de usuario">
              <Avatar className="h-10 w-10">
                <AvatarImage src={undefined} />
                <AvatarFallback>
                  {initials ? initials : <User className="h-5 w-5" />}
                </AvatarFallback>
              </Avatar>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>{displayName || "Usuario"}</DropdownMenuLabel>
            <DropdownMenuLabel className="text-xs font-normal text-muted-foreground">
              {displayEmail}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={logout}>
              Cerrar sesión
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
